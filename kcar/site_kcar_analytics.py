from kcar.site_kcar import TimeDealCar
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import asyncio
from aiogoogletrans import Translator
import torch
from transformers import AutoTokenizer, AutoModel, BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity

engine = create_async_engine("sqlite+aiosqlite:///../cars_2.db")
session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

translator = Translator()

# tokenizer = AutoTokenizer.from_pretrained('xlm-roberta-base')
# model = AutoModel.from_pretrained('xlm-roberta-base')

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')


def get_bert_embedding(text):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=128)

    with torch.no_grad():
        outputs = model(**inputs)

    return outputs.last_hidden_state[:, 0, :].numpy()


def compare_texts(value_origin, value_new):
    cnt_bad = 0
    cnt_good = 0
    for origin, new in zip(list(value_origin), value_new):
        embedding1 = get_bert_embedding(origin)
        embedding2 = get_bert_embedding(new)

        similarity = cosine_similarity(embedding1, embedding2)[0][0]

        if similarity >= 0.7:
            cnt_good += 1
        else:
            cnt_bad += 1

    print(f"Всего слов = {len(value_origin)}")
    print(f"Хороших переводов = {cnt_good}")
    print(f"Плохих переводов = {cnt_bad}")


async def translate_with_cache(text, src, dest):
    if not text.strip():
        return text
    try:
        translated = await translator.translate(text, src=src, dest=dest)
        return translated.text
    except Exception as e:
        print(f"Error translating '{text}': {e}")
        return text


async def translate_field_values(field, values, src, dest):
    tasks = [translate_with_cache(value, src, dest) for value in values if value.strip()]
    translated_values = await asyncio.gather(*tasks)
    return translated_values


async def translation(unique_values):
    fields_to_translate_ru = []
    fields_to_translate_en = ["car_mark", "car_model"]

    tasks = []
    for field, value_set in unique_values.items():
        if field in fields_to_translate_ru:
            tasks.append(
                asyncio.create_task(translate_field_values(field, value_set, src="ko", dest="ru"))
            )
        elif field in fields_to_translate_en:
            tasks.append(
                asyncio.create_task(translate_field_values(field, value_set, src="ko", dest="en"))
            )
        else:
            tasks.append(asyncio.create_task(asyncio.sleep(0)))  # Пропуск перевода

    # Выполнить все задачи параллельно
    results = await asyncio.gather(*tasks)

    # Обновить словарь с переводами
    for idx, field in enumerate(unique_values.keys()):
        unique_values[field] = results[idx]

    return unique_values


async def analytics():
    async with session_factory() as db_session:
        async with db_session.begin():
            result = await db_session.execute(select(TimeDealCar))
            cars = result.scalars().all()

            unique_values_mark = {}
            unique_values_model = {}

            for column in TimeDealCar.__table__.columns:
                field_name = column.name
                if field_name in ("car_mark",):
                    values_mark = [getattr(car, field_name) for car in cars if
                                   getattr(car, field_name) is not None and getattr(car, field_name)]
                    unique_values_mark[field_name] = set(values_mark)
                elif field_name in ("car_model",):
                    values_model = [getattr(car, field_name) for car in cars if
                                    getattr(car, field_name) is not None and getattr(car, field_name)]
                    unique_values_model[field_name] = set(values_model)

            unique_values_original_mark = unique_values_mark.copy()
            unique_values_original_model = unique_values_model.copy()

            updated_unique_values_mark = await translation(unique_values_mark)
            value_origin_mark = unique_values_original_mark['car_mark']
            value_new_mark = updated_unique_values_mark['car_mark']
            print("Марки:")
            compare_texts(value_origin_mark, value_new_mark)

            updated_unique_values_model = await translation(unique_values_model)
            value_origin_model = unique_values_original_model['car_model']
            value_new_model = updated_unique_values_model['car_model']
            print("Модели:")
            compare_texts(value_origin_model, value_new_model)


def main():
    asyncio.run(analytics())


if __name__ == '__main__':
    main()
