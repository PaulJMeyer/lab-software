import pytest

from app.domain.models import FragmentTemplate
from app.services.template_service import TemplateService


@pytest.fixture
def service():
    return TemplateService()


@pytest.fixture
def template_a():
    return FragmentTemplate(name="Gene X", recognition_sequence="ACGT", wildtype_sequence="TTTT")


@pytest.fixture
def template_b():
    return FragmentTemplate(name="Gene Y", recognition_sequence="GGGG", wildtype_sequence="CCCC")


class TestAddTemplate:

    def test_add_template_stored(self, service, template_a):
        service.add_template(template_a)
        assert service.find_template("Gene X") is template_a

    def test_add_duplicate_name_raises(self, service, template_a):
        service.add_template(template_a)
        duplicate = FragmentTemplate(name="Gene X", recognition_sequence="TTTT", wildtype_sequence="GGGG")
        with pytest.raises(ValueError):
            service.add_template(duplicate)


class TestListTemplates:

    def test_list_empty_service(self, service):
        assert service.list_templates() == []

    def test_list_returns_all_added_templates(self, service, template_a, template_b):
        service.add_template(template_a)
        service.add_template(template_b)
        templates = service.list_templates()
        assert len(templates) == 2
        assert template_a in templates
        assert template_b in templates


class TestFindTemplate:

    def test_find_unknown_name_returns_none(self, service):
        assert service.find_template("Unknown") is None


class TestState:

    def test_get_state_returns_internal_dict(self, service, template_a):
        service.add_template(template_a)
        assert service.get_state() == {"Gene X": template_a}

    def test_set_state_replaces_templates(self, service, template_a, template_b):
        service.add_template(template_a)
        service.set_state({"Gene Y": template_b})
        assert service.find_template("Gene X") is None
        assert service.find_template("Gene Y") is template_b
