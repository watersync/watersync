"""Detail forms for Deployment models."""

from django.forms import ModelForm

from watersync.sensor.models_detail import PressureSensorDeploymentDetail


class PressureSensorDeploymentDetailForm(ModelForm):
    """Form for pressure sensor deployment details.

    Used for both gauge pressure and absolute pressure deployments.
    """

    class Meta:
        model = PressureSensorDeploymentDetail
        fields = ["installation_elevation"]


# Mapping from deployment type to detail form class
DEPLOYMENT_TYPE_DETAIL_FORMS = {
    "gauge_pressure": PressureSensorDeploymentDetailForm,
    "absolute_pressure": PressureSensorDeploymentDetailForm,
    # "other" has no detail form
}
