import pytest

from app.domain.models import Sample
from app.services.lab_service import LabService


@pytest.fixture
def service():
    return LabService()


@pytest.fixture
def sample_a():
    return Sample("111111111", "ACGT")


@pytest.fixture
def sample_b():
    return Sample("222222222", "TTTT")


class TestAddSample:

    def test_add_sample_stored(self, service, sample_a):
        service.add_sample(sample_a)
        assert service.find_sample("111111111") is sample_a

    def test_add_duplicate_id_raises(self, service, sample_a):
        service.add_sample(sample_a)
        duplicate = Sample("111111111", "TTTT")
        with pytest.raises(ValueError):
            service.add_sample(duplicate)


class TestListSamples:

    def test_list_empty_service(self, service):
        assert service.list_samples() == []

    def test_list_returns_all_added_samples(self, service, sample_a, sample_b):
        service.add_sample(sample_a)
        service.add_sample(sample_b)
        assert set(service.list_samples()) == {sample_a, sample_b}


class TestUpdateSample:

    def test_update_replaces_dna(self, service, sample_a):
        service.add_sample(sample_a)
        updated = service.update_sample("111111111", "TTTT")
        assert updated.sample_dna == "TTTT"
        assert service.find_sample("111111111").sample_dna == "TTTT"

    def test_update_keeps_id_unchanged(self, service, sample_a):
        service.add_sample(sample_a)
        updated = service.update_sample("111111111", "TTTT")
        assert updated.sample_id == "111111111"

    def test_update_unknown_id_raises(self, service):
        with pytest.raises(ValueError):
            service.update_sample("999999999", "TTTT")

    def test_update_with_invalid_dna_raises(self, service, sample_a):
        service.add_sample(sample_a)
        with pytest.raises(ValueError):
            service.update_sample("111111111", "XYZ")


class TestDeleteSample:

    def test_delete_existing_sample(self, service, sample_a):
        service.add_sample(sample_a)
        service.delete_sample("111111111")
        assert service.find_sample("111111111") is None

    def test_delete_unknown_id_raises(self, service):
        with pytest.raises(ValueError):
            service.delete_sample("999999999")


class TestFindSample:

    def test_find_unknown_id_returns_none(self, service):
        assert service.find_sample("999999999") is None


class TestState:

    def test_get_state_returns_internal_dict(self, service, sample_a):
        service.add_sample(sample_a)
        state = service.get_state()
        assert state == {"111111111": sample_a}

    def test_set_state_replaces_samples(self, service, sample_a, sample_b):
        service.add_sample(sample_a)
        service.set_state({"222222222": sample_b})
        assert service.find_sample("111111111") is None
        assert service.find_sample("222222222") is sample_b
