from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime
from abc import ABCMeta, abstractmethod


class Serializable(metaclass=ABCMeta):
    @abstractmethod
    def serialize(self) -> Dict[str, Any]:
        return NotImplemented


@dataclass
class Cart(Serializable):
    id: int
    goods_amount: Dict[int, int]

    def serialize(self) -> Dict[str, Any]:
        return {'cart_id': self.id}

    __slots__ = ['id', 'goods_amount']


@dataclass(frozen=True)
class Category(Serializable):
    id: int
    category_name: str

    def serialize(self) -> Dict[str, Any]:
        return {
            'category_id': self.id,
            'category_name': f"'{self.category_name}'"
        }

    __slots__ = ['id', 'category_name']


@dataclass(frozen=True)
class Goods(Serializable):
    id: int
    category_id: int
    goods_name: str
    description: str = ''
    price: float = 0.0

    def serialize(self) -> Dict[str, Any]:
        return {
            'goods_id': self.id,
            'category_id': self.category_id,
            'goods_name': f"'{self.goods_name}'",
            'description': f"'{self.description}'",
            'price': self.price
        }

    __slots__ = ['id', 'category_id', 'goods_name']


@dataclass
class User(Serializable):
    id: int
    user_name: str
    last_ip: str
    country: str = 'Unknown'
    visits_count: int = 0
    carts_count: int = 0
    payments_count: int = 0

    def serialize(self) -> Dict[str, Any]:
        return {
            'user_id': self.id,
            'user_name': f"'{self.user_name}'",
            'country': f"'{self.country}'",
            'visits_count': self.visits_count,
            'carts_count': self.carts_count,
            'payments_count': self.payments_count,
            'last_ip': f"'{self.last_ip}'"
        }

    def __eq__(self, other: 'User') -> bool:
        return (self.id == other.id and
                self.user_name == other.user_name and
                self.last_ip == other.last_ip and
                self.visits_count == other.visits_count and
                self.carts_count == other.carts_count and
                self.payments_count == other.payments_count
                )

    __slots__ = ['id', 'user_name', 'last_ip']


@dataclass(frozen=True)
class Transaction(Serializable):
    id: int
    user_id: int
    created_at: datetime

    def serialize(self) -> Dict[str, Any]:
        return {
            'transaction_id': self.id,
            'user_id': self.user_id,
            'created_at_d': f"'{self.created_at.date()}'",
            'created_at_t': f"'{self.created_at.time().replace(microsecond=0)}'"
        }

    __slots__ = ['id', 'user_id', 'created_at']


@dataclass(frozen=True)
class TransactionGoods(Serializable):
    id: int
    transaction_id: int
    goods_id: int
    count: int = 1
    total_price: float = 0.0

    def serialize(self) -> Dict[str, Any]:
        return {
            'transactions_goods_id': self.id,
            'transaction_id': self.transaction_id,
            'goods_id': self.goods_id,
            'goods_count': self.count,
            'total_price': self.total_price
        }

    __slots__ = ['id', 'transaction_id', 'goods_id']


@dataclass(frozen=True)
class CategoriesVisit(Serializable):
    id: int
    category_id: int
    visited_at: datetime
    visitor_ip: str
    visitor_country: str = 'Unknown'

    def serialize(self) -> Dict[str, Any]:
        return {
            'categories_visits': self.id,
            'category_id': self.category_id,
            'visitor_ip': f"'{self.visitor_ip}'",
            'visitor_country': f"'{self.visitor_country}'",
            'visited_at_d': f"'{self.visited_at.date()}'",
            'visited_at_t': f"'{self.visited_at.time().replace(microsecond=0)}'"
        }

    def __eq__(self, other: 'CategoriesVisit') -> bool:
        return (self.id == other.id and
                self.category_id == other.category_id and
                self.visitor_ip == other.visitor_ip and
                self.visited_at == other.visited_at
                )

    __slots__ = ['id', 'category_id', 'visited_at', 'visitor_ip']


@dataclass(frozen=True)
class Query(Serializable):
    id: int
    ip: str
    text: str
    queried_at: datetime

    def serialize(self) -> Dict[str, Any]:
        return {
            'query_id': self.id,
            'query_ip': f"'{self.ip}'",
            'query_text': f"'{self.text}'",
            'queried_at_d': f"'{self.queried_at.date()}'",
            'queried_at_t': f"'{self.queried_at.time().replace(microsecond=0)}'"
        }

    __slots__ = ['id', 'ip', 'text', 'queried_at']
