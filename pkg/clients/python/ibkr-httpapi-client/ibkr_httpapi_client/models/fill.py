from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.contract import Contract
    from ..models.fill_commission_report_type_0 import FillCommissionReportType0
    from ..models.fill_execution import FillExecution


T = TypeVar("T", bound="Fill")


@_attrs_define
class Fill:
    """
    Attributes:
        contract (Contract | Unset):
        execution (FillExecution | Unset):
        commission_report (FillCommissionReportType0 | None | Unset):
        time (str | Unset):
    """

    contract: Contract | Unset = UNSET
    execution: FillExecution | Unset = UNSET
    commission_report: FillCommissionReportType0 | None | Unset = UNSET
    time: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.fill_commission_report_type_0 import FillCommissionReportType0

        contract: dict[str, Any] | Unset = UNSET
        if not isinstance(self.contract, Unset):
            contract = self.contract.to_dict()

        execution: dict[str, Any] | Unset = UNSET
        if not isinstance(self.execution, Unset):
            execution = self.execution.to_dict()

        commission_report: dict[str, Any] | None | Unset
        if isinstance(self.commission_report, Unset):
            commission_report = UNSET
        elif isinstance(self.commission_report, FillCommissionReportType0):
            commission_report = self.commission_report.to_dict()
        else:
            commission_report = self.commission_report

        time = self.time

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if contract is not UNSET:
            field_dict["contract"] = contract
        if execution is not UNSET:
            field_dict["execution"] = execution
        if commission_report is not UNSET:
            field_dict["commissionReport"] = commission_report
        if time is not UNSET:
            field_dict["time"] = time

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.contract import Contract
        from ..models.fill_commission_report_type_0 import FillCommissionReportType0
        from ..models.fill_execution import FillExecution

        d = dict(src_dict)
        _contract = d.pop("contract", UNSET)
        contract: Contract | Unset
        if isinstance(_contract, Unset):
            contract = UNSET
        else:
            contract = Contract.from_dict(_contract)

        _execution = d.pop("execution", UNSET)
        execution: FillExecution | Unset
        if isinstance(_execution, Unset):
            execution = UNSET
        else:
            execution = FillExecution.from_dict(_execution)

        def _parse_commission_report(data: object) -> FillCommissionReportType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                commission_report_type_0 = FillCommissionReportType0.from_dict(data)

                return commission_report_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(FillCommissionReportType0 | None | Unset, data)

        commission_report = _parse_commission_report(d.pop("commissionReport", UNSET))

        time = d.pop("time", UNSET)

        fill = cls(
            contract=contract,
            execution=execution,
            commission_report=commission_report,
            time=time,
        )

        fill.additional_properties = d
        return fill

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
