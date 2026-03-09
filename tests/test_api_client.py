"""Tests for PRE Distribuce API client."""

import pytest
from aiohttp import ClientSession
from aioresponses import aioresponses

from custom_components.pre_hdo.api_client import PreHdoApiClient, PreHdoApiError
from custom_components.pre_hdo.const import HDO_MULTI_DAY_URL, HDO_ONE_DAY_URL


class TestPreHdoApiClient:
    @pytest.mark.asyncio
    async def test_fetch_hdo_returns_periods(self, sample_hdo_json) -> None:
        async with ClientSession() as session:
            client = PreHdoApiClient(session=session)
            with aioresponses() as mock:
                mock.post(HDO_ONE_DAY_URL, payload=sample_hdo_json)
                periods = await client.async_get_hdo_periods("492")
                assert len(periods) == 5
                assert periods[0].tariff == "VT"
                assert periods[1].tariff == "NT"

    @pytest.mark.asyncio
    async def test_fetch_hdo_with_specific_date(self, sample_hdo_json) -> None:
        async with ClientSession() as session:
            client = PreHdoApiClient(session=session)
            with aioresponses() as mock:
                mock.post(HDO_ONE_DAY_URL, payload=sample_hdo_json)
                periods = await client.async_get_hdo_periods(
                    "492", date_str="13.02.2026"
                )
                assert len(periods) == 5

    @pytest.mark.asyncio
    async def test_fetch_hdo_http_error_raises(self) -> None:
        async with ClientSession() as session:
            client = PreHdoApiClient(session=session)
            with aioresponses() as mock:
                mock.post(HDO_ONE_DAY_URL, status=500)
                with pytest.raises(PreHdoApiError):
                    await client.async_get_hdo_periods("492")

    @pytest.mark.asyncio
    async def test_fetch_hdo_invalid_json_raises(self) -> None:
        async with ClientSession() as session:
            client = PreHdoApiClient(session=session)
            with aioresponses() as mock:
                mock.post(HDO_ONE_DAY_URL, body="not json")
                with pytest.raises(PreHdoApiError):
                    await client.async_get_hdo_periods("492")

    @pytest.mark.asyncio
    async def test_validate_command_id_valid(self, sample_hdo_json) -> None:
        async with ClientSession() as session:
            client = PreHdoApiClient(session=session)
            with aioresponses() as mock:
                mock.post(HDO_ONE_DAY_URL, payload=sample_hdo_json)
                result = await client.async_validate_command_id("492")
                assert result is True

    @pytest.mark.asyncio
    async def test_validate_command_id_invalid(self) -> None:
        async with ClientSession() as session:
            client = PreHdoApiClient(session=session)
            with aioresponses() as mock:
                mock.post(HDO_ONE_DAY_URL, payload={"html": ""})
                result = await client.async_validate_command_id("999")
                assert result is False


class TestPreHdoApiClientMultiDay:
    @pytest.mark.asyncio
    async def test_fetch_multi_day_returns_schedules(
        self, sample_multi_day_json
    ) -> None:
        async with ClientSession() as session:
            client = PreHdoApiClient(session=session)
            with aioresponses() as mock:
                mock.post(HDO_MULTI_DAY_URL, payload=sample_multi_day_json)
                schedules = await client.async_get_hdo_multi_day("492")
                assert len(schedules) == 2
                assert len(schedules[0].periods) == 5

    @pytest.mark.asyncio
    async def test_fetch_multi_day_http_error_raises(self) -> None:
        async with ClientSession() as session:
            client = PreHdoApiClient(session=session)
            with aioresponses() as mock:
                mock.post(HDO_MULTI_DAY_URL, status=500)
                with pytest.raises(PreHdoApiError):
                    await client.async_get_hdo_multi_day("492")
