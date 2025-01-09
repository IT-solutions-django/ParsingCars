from utils.db import Car, Session, Mark, Model


def get_unique_marks():
    session = Session()

    marks_all = session.query(Car.car_mark).distinct().all()

    marks_unique = [Mark(name=mark_unique) for mark_unique in marks_all]

    session.add_all(marks_unique)


def get_unique_models():
    session = Session()

    unique_marks = session.query(Mark).all()


