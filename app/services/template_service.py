from app.domain.models import FragmentTemplate


class TemplateService:
    def __init__(self):
        # template name -> FragmentTemplate
        self._templates = {}

    def add_template(self, template: FragmentTemplate):
        if template.name in self._templates:
            raise ValueError(f"Template name already exists: {template.name}")

        self._templates[template.name] = template

    def list_templates(self):
        return list(self._templates.values())

    def find_template(self, name: str):
        return self._templates.get(name, None)

    def get_state(self):
        return self._templates

    def set_state(self, templates_dict):
        self._templates = templates_dict
