from __future__ import annotations
from typing import Protocol
from sbilifeco.models.base import Response


class BaseVectoriser:
    def __init__(self):
        self.vectoriser_listeners: list[IVectoriserListener] = []

    def add_vectoriser_listener(self, listener: IVectoriserListener) -> BaseVectoriser:
        self.vectoriser_listeners.append(listener)
        return self

    async def vectorise(
        self, request_id: str, material: str | bytes | bytearray
    ) -> Response[list[float | int]]:
        """
        Vectorise the given material.
        Args:
            request_id (str): A request ID that uniquely identifies this request and is useful when using listeners.
            material (str | bytes | bytearray): The material to vectorise.
        """
        raise NotImplementedError()


class IVectoriserListener(Protocol):
    async def on_vectorised(
        self,
        request_id: str,
        response: Response[list[float | int]],
    ) -> None:
        """
        Called when a material has been vectorised.
        Args:
            request_id (str): The request ID for which this result is relevant.
            response (Response[list[float | int]]): The response that contains the vectorised material.
        """
        ...
