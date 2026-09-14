"""Contrato read-only implementado por integrações de marketplace."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping, Sequence

from contracts.inventory_snapshot import InventorySnapshot, Marketplace


class IntegrationNotConfiguredError(RuntimeError):
    pass


class IntegrationUnavailableError(RuntimeError):
    pass


class MarketplaceAdapter(ABC):
    """Boundary entre o MyStock e uma API externa.

    O contrato expõe somente leitura. Operações de criação, exclusão ou alteração
    de estoque não fazem parte desta interface.
    """

    @property
    @abstractmethod
    def marketplace(self) -> Marketplace:
        raise NotImplementedError

    @abstractmethod
    def authenticate(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_account(self) -> Mapping[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_inventory(self) -> Sequence[InventorySnapshot]:
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        raise NotImplementedError
