import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import os
from dotenv import load_dotenv
from os.path import join, dirname
from sqlalchemy import func as alchemyFn
from datetime import datetime

Base = declarative_base()

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


class publisher(Base):
    __tablename__ = "publisher"

    id = sq.Column(sq.Integer, autoincrement=True, primary_key=True)
    name = sq.Column(sq.String(length=50), nullable=False)

    def __str__(self):
        return f'publisher id: {self.id}, publisher name: {self.name}'


class book(Base):
    __tablename__ = "book"

    id = sq.Column(sq.Integer, autoincrement=True, primary_key=True)
    title = sq.Column(sq.String(length=50), nullable=False)
    id_publisher = sq.Column(sq.Integer, sq.ForeignKey("publisher.id"), nullable=False)
    publisher = relationship(publisher, backref="book")

    def __str__(self):
        return f'book id: {self.id}, book title: {self.title}, id_publisher: {self.id_publisher}'


class shop(Base):
    __tablename__ = "shop"

    id = sq.Column(sq.Integer, autoincrement=True, primary_key=True)
    name = sq.Column(sq.String(length=30), nullable=False)

    def __str__(self):
        return f'shop id: {self.id}, shop name: {self.name}'


class stock(Base):
    __tablename__ = "stock"

    id = sq.Column(sq.Integer, autoincrement=True, primary_key=True)
    id_shop = sq.Column(sq.Integer, sq.ForeignKey('shop.id'), nullable=False)
    id_book = sq.Column(sq.Integer, sq.ForeignKey('book.id'), nullable=False)
    shop = relationship(shop, backref='stock')
    book = relationship(book, backref='stock')
    count = sq.Column(sq.Integer, nullable=False)

    def __str__(self):
        return f'stock id: {self.id}, id_shop: {self.id_shop}, id_book: {self.id_book}, count: {self.count}'


class sale(Base):
    __tablename__ = "sale"

    id = sq.Column(sq.Integer, autoincrement=True, primary_key=True)
    price = sq.Column(sq.Float, nullable=False)
    date_sale = sq.Column(sq.DateTime, nullable=False, default=datetime.now)
    id_stock = sq.Column(sq.Integer, sq.ForeignKey("stock.id"), nullable=False)
    count = sq.Column(sq.Integer, nullable=False)
    stock = relationship(stock, backref='sale')

    def __str__(self):
        return f'id: {self.id}, price: {self.price}, id_stock: {self.id_stock}, date_sale: {self.date_sale}, count:{self.count}'


def check_publisher(name):
    q = session.query(publisher).filter(alchemyFn.lower(publisher.name) == name.lower()).all()
    if not q:
        return True
    else:
        return False


def add_publisher(name):
    if check_publisher(name):
        new_publisher = publisher(name=name)
        session.add(new_publisher)
        session.commit()
    else:
        print(f"Автор {name} уже внесен в базу")


def check_book(title, id_publisher):
    q = session.query(book).filter(alchemyFn.lower(book.title) == title.lower(), id_publisher == id_publisher).all()
    if not q:
        return True
    else:
        return False


def add_book(title, id_publisher):
    if check_book(title, id_publisher):
        new_book = book(title=title, id_publisher=id_publisher)
        session.add(new_book)
        session.commit()
    else:
        print(f"Книга {title} уже внесена в базу")


def check_shop(name):
    q = session.query(shop).filter(alchemyFn.lower(shop.name) == name.lower()).all()
    if not q:
        return True
    else:
        return False


def add_shop(name):
    if check_shop(name):
        new_shop = shop(name=name)
        session.add(new_shop)
        session.commit()
    else:
        print(f"Магазин {name} уже введен в базу")


def check_stok(id_shop, id_book):
    q = session.query(stock).filter(stock.id_shop == id_shop, stock.id_book == id_book).all()
    if not q:
        return True
    else:
        return False


def add_stock(id_shop, id_book, count):
    if check_stok(id_shop, id_book):
        new_stock = stock(id_shop=id_shop, id_book=id_book, count=count)
        session.add(new_stock)
        session.commit()
    else:
        print("Книга уже продается в данном магазине")


def check_sale(id_stock, count):
    q = session.query(stock).filter(stock.id == id_stock).all()
    if q:
        if q[0].count >= count:
            return True
        else:
            stock_count = session.query(stock).filter(stock.id == id_stock).all()[0].count
            print(f"В остатке недостаточное количество книг. В остатке {stock_count} штук(а)")
            return False
    else:
        print(f"id_stock {id_stock} не существует")


def add_sale(price, id_stock, count):
    if check_sale(id_stock, count):
        new_sale = sale(price=price, id_stock=id_stock, count=count)
        session.query(stock).filter(stock.id == id_stock).update({stock.count: stock.count - count})
        session.add(new_sale)
        session.commit()


def get_publisher_data(publiher_):
    data = session.query(
        publisher.name,
        book.title,
        shop.name,
        sale.price,
        sale.date_sale
    ).join(book).join(stock).join(shop).join(sale).filter(
        (alchemyFn.lower(publisher.name)).like(f"%{publiher_}%")
    ).all()
    return data


def create_tables(engine):
    Base.metadata.create_all(engine)


def delete_tables(engine):
    Base.metadata.drop_all(engine)


DSN = os.environ.get("DSN")
engine = sq.create_engine(DSN)

Session = sessionmaker(bind=engine)
session = Session()

delete_tables(engine)

create_tables(engine)

add_publisher(name="Александр Сергеевич Пушкин")
add_publisher(name="Лев Николаевич Толстой")

add_book(title="Руслан и Людмила", id_publisher=1)
add_book(title="Капитанская дочка", id_publisher=1)
add_book(title="Евгений Онегин", id_publisher=1)

add_book(title="После бала", id_publisher=2)
add_book(title="Война и Мир", id_publisher=2)
add_book(title="Анна Каренина", id_publisher=2)

add_shop(name="Буквоед")
add_shop(name="Лабиринт")
add_shop(name="Книжный дом")

add_stock(id_shop=1, id_book=1, count=10)
add_stock(id_shop=2, id_book=1, count=2)

add_stock(id_shop=1, id_book=2, count=7)
add_stock(id_shop=2, id_book=2, count=5)
add_stock(id_shop=3, id_book=2, count=1)

add_stock(id_shop=2, id_book=3, count=8)
add_stock(id_shop=3, id_book=3, count=2)

add_stock(id_shop=1, id_book=4, count=4)
add_stock(id_shop=2, id_book=5, count=7)
add_stock(id_shop=2, id_book=6, count=11)

add_sale(price=450, id_stock=1, count=1)
add_sale(price=380, id_stock=2, count=1)
add_sale(price=500, id_stock=3, count=2)
add_sale(price=490, id_stock=4, count=2)
add_sale(price=520, id_stock=5, count=1)
add_sale(price=420, id_stock=6, count=2)
add_sale(price=520, id_stock=7, count=1)
add_sale(price=620, id_stock=8, count=1)
add_sale(price=560, id_stock=9, count=1)
add_sale(price=550, id_stock=10, count=3)


if __name__ == '__main__':
    publiher_ = input('Введите автора:').lower()
    data = get_publisher_data(publiher_)
    if data:
        for item in data:
            title = item[1]
            shop = item[2]
            price = item[3]
            date = datetime.strftime(item[4], f'%d-%m-%Y')
            print(f'{title:<50} | {shop:<30} | {price:<10} | {date}')
    else:
        print(f"Автор {publiher_} отсутствует в базе")

session.close()
