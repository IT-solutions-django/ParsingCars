from autohub.site_autohub import TimeDealCar
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import asyncio
from aiogoogletrans import Translator
import torch
from transformers import BertTokenizer, BertModel, AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity

engine = create_async_engine("sqlite+aiosqlite:///../cars_2.db")
session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

translator = Translator()

# tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
# model = BertModel.from_pretrained('bert-base-uncased')

tokenizer = AutoTokenizer.from_pretrained('xlm-roberta-base')
model = AutoModel.from_pretrained('xlm-roberta-base')


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

            unique_values = {}

            for column in TimeDealCar.__table__.columns:
                field_name = column.name
                if field_name in ("car_mark", "car_model"):
                    values = [getattr(car, field_name) for car in cars]
                    unique_values[field_name] = set(values)

            unique_values_original = unique_values.copy()

            updated_unique_values = await translation(unique_values)
            print(updated_unique_values)

            # value_origin = unique_values_original['car_name']
            # value_new = updated_unique_values['car_name']
            #
            # compare_texts(value_origin, value_new)


def main():
    asyncio.run(analytics())


if __name__ == '__main__':
    main()
