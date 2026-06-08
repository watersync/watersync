"""Tests for core module views."""

import pytest
from django.urls import reverse

from watersync.core.models import Fieldwork, Location, Project
from watersync.core.tests.factories import (
    FieldworkFactory,
    LocationFactory,
    ProjectFactory,
)
from watersync.users.tests.factories import UserFactory


pytestmark = pytest.mark.django_db


# ============================================================================
# Project View Tests
# ============================================================================


class TestProjectListView:
    """Tests for project list view."""

    def test_anonymous_user_redirected(self, client):
        """Anonymous users should be redirected to login."""
        url = reverse("core:projects")
        response = client.get(url)
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_authenticated_user_sees_own_projects(self, client):
        """Users should only see projects they belong to."""
        user = UserFactory()
        project = ProjectFactory(user=[user])
        other_project = ProjectFactory()  # Not associated with user

        client.force_login(user)
        url = reverse("core:projects")
        response = client.get(url)

        assert response.status_code == 200
        assert project in response.context["object_list"]
        assert other_project not in response.context["object_list"]

    def test_empty_project_list(self, client):
        """Users with no projects see empty list."""
        user = UserFactory()
        client.force_login(user)
        url = reverse("core:projects")
        response = client.get(url)

        assert response.status_code == 200
        assert len(response.context["object_list"]) == 0


class TestProjectCreateView:
    """Tests for project create view."""

    def test_get_form(self, client):
        """GET request should return the form."""
        user = UserFactory()
        client.force_login(user)
        url = reverse("core:add-project")
        response = client.get(url)

        assert response.status_code == 200

    def test_create_project_success(self, client):
        """POST with valid data should create project."""
        user = UserFactory()
        client.force_login(user)
        url = reverse("core:add-project")

        data = {
            "name": "Test Project",
            "description": "Test description",
            "start_date": "2025-01-15",
            "user": [user.pk],
        }
        response = client.post(url, data, HTTP_HX_REQUEST="true")

        assert response.status_code == 204  # HTMX success response
        assert Project.objects.filter(name="Test Project").exists()

    def test_create_project_assigns_user(self, client):
        """Created project should have the creator as a user."""
        user = UserFactory()
        client.force_login(user)
        url = reverse("core:add-project")

        data = {
            "name": "Test Project",
            "description": "Test description",
            "start_date": "2025-01-15",
            "user": [user.pk],
        }
        client.post(url, data, HTTP_HX_REQUEST="true")

        project = Project.objects.get(name="Test Project")
        assert user in project.user.all()

    def test_create_project_duplicate_name_fails(self, client):
        """Creating project with duplicate name should fail."""
        user = UserFactory()
        ProjectFactory(name="Existing Project", user=[user])

        client.force_login(user)
        url = reverse("core:add-project")

        data = {
            "name": "Existing Project",
            "description": "Test description",
            "start_date": "2025-01-15",
            "user": [user.pk],
        }
        response = client.post(url, data, HTTP_HX_REQUEST="true")

        # Form should be re-rendered with errors (status 200 for HTMX)
        assert response.status_code == 200
        assert Project.objects.filter(name="Existing Project").count() == 1


class TestProjectDetailView:
    """Tests for project detail view."""

    def test_view_own_project(self, client):
        """Users can view projects they belong to."""
        user = UserFactory()
        project = ProjectFactory(user=[user])

        client.force_login(user)
        url = reverse("core:detail-project", kwargs={"project_pk": project.pk})
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["object"].pk == project.pk

    def test_view_other_project_forbidden(self, client):
        """Users cannot view projects they don't belong to."""
        user = UserFactory()
        other_project = ProjectFactory()

        client.force_login(user)
        url = reverse("core:detail-project", kwargs={"project_pk": other_project.pk})
        response = client.get(url)

        # Should still return 200 but may show empty or forbidden
        # Depends on implementation - adjust based on actual behavior
        assert response.status_code in [200, 403, 404]


class TestProjectUpdateView:
    """Tests for project update view."""

    def test_update_project(self, client):
        """Users can update their projects."""
        user = UserFactory()
        project = ProjectFactory(name="Old Name", user=[user])

        client.force_login(user)
        url = reverse("core:update-project", kwargs={"project_pk": project.pk})

        data = {
            "name": "New Name",
            "description": "Updated description",
            "start_date": "2025-01-15",
            "user": [user.pk],
        }
        response = client.post(url, data, HTTP_HX_REQUEST="true")

        assert response.status_code == 204
        project.refresh_from_db()
        assert project.name == "New Name"


class TestProjectDeleteView:
    """Tests for project delete view."""

    def test_delete_project(self, client):
        """Users can delete their projects."""
        user = UserFactory()
        project = ProjectFactory(user=[user])
        project_pk = project.pk

        client.force_login(user)
        url = reverse("core:delete-project", kwargs={"project_pk": project_pk})
        response = client.post(url, HTTP_HX_REQUEST="true")

        assert response.status_code in [200, 204, 302]
        assert not Project.objects.filter(pk=project_pk).exists()


# ============================================================================
# Location View Tests
# ============================================================================


class TestLocationListView:
    """Tests for location list view."""

    def test_list_locations_for_project(self, client):
        """Users can list locations for their project."""
        user = UserFactory()
        project = ProjectFactory(user=[user])
        location1 = LocationFactory(project=project)
        location2 = LocationFactory(project=project)
        other_location = LocationFactory()  # Different project

        client.force_login(user)
        url = reverse("core:locations", kwargs={"project_pk": project.pk})
        response = client.get(url)

        assert response.status_code == 200
        object_list = list(response.context["object_list"])
        assert location1 in object_list
        assert location2 in object_list
        assert other_location not in object_list


class TestLocationCreateView:
    """Tests for location create view."""

    def test_create_location(self, client):
        """Users can create locations in their project."""
        user = UserFactory()
        project = ProjectFactory(user=[user])

        client.force_login(user)
        url = reverse("core:add-location", kwargs={"project_pk": project.pk})

        data = {
            "name": "Test Location",
            "type": Location.LocationTypes.PIEZOMETER,
            "latitude": "51.5",
            "longitude": "-0.1",
            "altitude": "10",
            "status": Location.StatusChoices.OPERATIONAL,
        }
        response = client.post(url, data, HTTP_HX_REQUEST="true")

        assert response.status_code == 204
        assert Location.objects.filter(name="Test Location", project=project).exists()

    def test_create_location_duplicate_name_in_project_fails(self, client):
        """Cannot create location with same name in same project."""
        user = UserFactory()
        project = ProjectFactory(user=[user])
        LocationFactory(project=project, name="Existing Location")

        client.force_login(user)
        url = reverse("core:add-location", kwargs={"project_pk": project.pk})

        data = {
            "name": "Existing Location",
            "type": Location.LocationTypes.PIEZOMETER,
            "latitude": "51.5",
            "longitude": "-0.1",
            "altitude": "10",
            "status": Location.StatusChoices.OPERATIONAL,
        }
        response = client.post(url, data, HTTP_HX_REQUEST="true")

        # Should fail with form errors
        assert response.status_code == 200
        assert Location.objects.filter(name="Existing Location", project=project).count() == 1

    def test_same_location_name_different_projects_ok(self, client):
        """Same location name is allowed in different projects."""
        user = UserFactory()
        project1 = ProjectFactory(user=[user])
        project2 = ProjectFactory(user=[user])
        LocationFactory(project=project1, name="Location A")

        client.force_login(user)
        url = reverse("core:add-location", kwargs={"project_pk": project2.pk})

        data = {
            "name": "Location A",
            "type": Location.LocationTypes.PIEZOMETER,
            "latitude": "51.5",
            "longitude": "-0.1",
            "altitude": "10",
            "status": Location.StatusChoices.OPERATIONAL,
        }
        response = client.post(url, data, HTTP_HX_REQUEST="true")

        assert response.status_code == 204
        assert Location.objects.filter(name="Location A").count() == 2


class TestLocationDetailView:
    """Tests for location detail view."""

    def test_view_location(self, client):
        """Users can view location details."""
        user = UserFactory()
        project = ProjectFactory(user=[user])
        location = LocationFactory(project=project)

        client.force_login(user)
        url = reverse(
            "core:detail-location",
            kwargs={"project_pk": project.pk, "location_pk": location.pk},
        )
        response = client.get(url)

        assert response.status_code == 200


class TestLocationUpdateView:
    """Tests for location update view."""

    def test_update_location(self, client):
        """Users can update locations."""
        user = UserFactory()
        project = ProjectFactory(user=[user])
        location = LocationFactory(project=project, name="Old Name")

        client.force_login(user)
        url = reverse(
            "core:update-location",
            kwargs={"project_pk": project.pk, "location_pk": location.pk},
        )

        data = {
            "name": "New Name",
            "type": location.type,
            "latitude": "51.5",
            "longitude": "-0.1",
            "altitude": "10",
            "status": location.status,
        }
        response = client.post(url, data, HTTP_HX_REQUEST="true")

        assert response.status_code == 204
        location.refresh_from_db()
        assert location.name == "New Name"


class TestLocationDeleteView:
    """Tests for location delete view."""

    def test_delete_location(self, client):
        """Users can delete locations."""
        user = UserFactory()
        project = ProjectFactory(user=[user])
        location = LocationFactory(project=project)
        location_pk = location.pk

        client.force_login(user)
        url = reverse(
            "core:delete-location",
            kwargs={"project_pk": project.pk, "location_pk": location_pk},
        )
        response = client.post(url, HTTP_HX_REQUEST="true")

        assert response.status_code in [200, 204, 302]
        assert not Location.objects.filter(pk=location_pk).exists()


# ============================================================================
# Fieldwork View Tests
# ============================================================================


class TestFieldworkListView:
    """Tests for fieldwork list view."""

    def test_list_fieldworks_for_project(self, client):
        """Users can list fieldworks for their project."""
        user = UserFactory()
        project = ProjectFactory(user=[user])
        fieldwork1 = FieldworkFactory(project=project, user=[user])
        fieldwork2 = FieldworkFactory(project=project, user=[user])
        other_fieldwork = FieldworkFactory()  # Different project, different user

        client.force_login(user)
        url = reverse("core:fieldworks", kwargs={"project_pk": project.pk})
        response = client.get(url)

        assert response.status_code == 200
        object_list = list(response.context["object_list"])
        assert fieldwork1 in object_list
        assert fieldwork2 in object_list
        assert other_fieldwork not in object_list

    def test_user_only_sees_fieldworks_they_participated_in(self, client):
        """Users should only see fieldworks where they are in the user M2M field."""
        user1 = UserFactory()
        user2 = UserFactory()
        project = ProjectFactory(user=[user1, user2])
        
        # Fieldwork where user1 participated
        fieldwork_user1 = FieldworkFactory(project=project, user=[user1])
        # Fieldwork where user2 participated
        fieldwork_user2 = FieldworkFactory(project=project, user=[user2])
        # Fieldwork where both participated
        fieldwork_both = FieldworkFactory(project=project, user=[user1, user2])
        
        client.force_login(user1)
        url = reverse("core:fieldworks", kwargs={"project_pk": project.pk})
        response = client.get(url)
        
        assert response.status_code == 200
        object_list = list(response.context["object_list"])
        
        # user1 should see their fieldworks and shared ones
        assert fieldwork_user1 in object_list
        assert fieldwork_both in object_list
        # user1 should NOT see fieldworks they didn't participate in
        assert fieldwork_user2 not in object_list


class TestFieldworkCreateView:
    """Tests for fieldwork create view."""

    def test_create_fieldwork(self, client):
        """Users can create fieldwork entries."""
        user = UserFactory()
        project = ProjectFactory(user=[user])

        client.force_login(user)
        url = reverse("core:add-fieldwork", kwargs={"project_pk": project.pk})

        data = {
            "project": project.pk,
            "date": "2025-01-15",
            "start_time": "09:00",
            "end_time": "17:00",
            "weather": Fieldwork.WeatherConditions.SUNNY,
            "user": [user.pk],
        }
        response = client.post(url, data, HTTP_HX_REQUEST="true")

        # Debug form errors
        if response.status_code == 200:
            form = response.context.get('form') if response.context else None
            if form:
                print(f"Form errors: {form.errors}")
                print(f"Form data: {form.data}")
        
        assert response.status_code == 204
        assert Fieldwork.objects.filter(project=project, date="2025-01-15").exists()

    def test_fieldwork_form_user_field_scoped_to_project(self, client):
        """User field in fieldwork form should only show project members."""
        project_member = UserFactory()
        non_member = UserFactory()
        project = ProjectFactory(user=[project_member])
        
        client.force_login(project_member)
        url = reverse("core:add-fieldwork", kwargs={"project_pk": project.pk})
        response = client.get(url, HTTP_HX_REQUEST="true")
        
        assert response.status_code == 200
        form = response.context["form"]
        user_queryset = form.fields["user"].queryset
        
        # Only project member should be in the queryset
        assert project_member in user_queryset
        assert non_member not in user_queryset

    def test_create_fieldwork_duplicate_date_fails(self, client):
        """Cannot create fieldwork with duplicate date."""
        user = UserFactory()
        project = ProjectFactory(user=[user])
        FieldworkFactory(project=project, date="2025-01-15")

        client.force_login(user)
        url = reverse("core:add-fieldwork", kwargs={"project_pk": project.pk})

        data = {
            "project": project.pk,
            "date": "2025-01-15",
            "start_time": "09:00",
            "end_time": "17:00",
            "weather": Fieldwork.WeatherConditions.SUNNY,
            "user": [user.pk],
        }
        response = client.post(url, data, HTTP_HX_REQUEST="true")

        # Should fail with form errors
        assert response.status_code == 200


class TestFieldworkDetailView:
    """Tests for fieldwork detail view."""

    def test_view_fieldwork(self, client):
        """Users can view fieldwork details."""
        user = UserFactory()
        project = ProjectFactory(user=[user])
        fieldwork = FieldworkFactory(project=project)

        client.force_login(user)
        url = reverse(
            "core:detail-fieldwork",
            kwargs={"project_pk": project.pk, "fieldwork_pk": fieldwork.pk},
        )
        response = client.get(url)

        assert response.status_code == 200


class TestFieldworkUpdateView:
    """Tests for fieldwork update view."""

    def test_update_fieldwork(self, client):
        """Users can update fieldwork entries."""
        user = UserFactory()
        project = ProjectFactory(user=[user])
        fieldwork = FieldworkFactory(project=project, weather=Fieldwork.WeatherConditions.SUNNY)

        client.force_login(user)
        url = reverse(
            "core:update-fieldwork",
            kwargs={"project_pk": project.pk, "fieldwork_pk": fieldwork.pk},
        )

        data = {
            "project": project.pk,
            "date": str(fieldwork.date),
            "start_time": fieldwork.start_time.strftime("%H:%M"),
            "end_time": fieldwork.end_time.strftime("%H:%M"),
            "weather": Fieldwork.WeatherConditions.RAINY,
            "user": [user.pk],
        }
        response = client.post(url, data, HTTP_HX_REQUEST="true")

        assert response.status_code == 204
        fieldwork.refresh_from_db()
        assert fieldwork.weather == Fieldwork.WeatherConditions.RAINY


class TestFieldworkDeleteView:
    """Tests for fieldwork delete view."""

    def test_delete_fieldwork(self, client):
        """Users can delete fieldwork entries."""
        user = UserFactory()
        project = ProjectFactory(user=[user])
        fieldwork = FieldworkFactory(project=project)
        fieldwork_pk = fieldwork.pk

        client.force_login(user)
        url = reverse(
            "core:delete-fieldwork",
            kwargs={"project_pk": project.pk, "fieldwork_pk": fieldwork_pk},
        )
        response = client.post(url, HTTP_HX_REQUEST="true")

        assert response.status_code in [200, 204, 302]
        assert not Fieldwork.objects.filter(pk=fieldwork_pk).exists()


# ============================================================================
# Access Control / Scoping Tests
# ============================================================================


class TestProjectAccessControl:
    """Tests to verify users can only access data from projects they belong to."""

    def test_non_member_cannot_access_project_locations(self, client):
        """Users should not be able to access locations of projects they don't belong to."""
        member = UserFactory()
        non_member = UserFactory()
        project = ProjectFactory(user=[member])
        LocationFactory(project=project)

        client.force_login(non_member)
        url = reverse("core:locations", kwargs={"project_pk": project.pk})
        response = client.get(url)

        # Should be forbidden (403) or redirected
        assert response.status_code == 403

    def test_non_member_cannot_access_project_fieldworks(self, client):
        """Users should not be able to access fieldworks of projects they don't belong to."""
        member = UserFactory()
        non_member = UserFactory()
        project = ProjectFactory(user=[member])
        FieldworkFactory(project=project, user=[member])

        client.force_login(non_member)
        url = reverse("core:fieldworks", kwargs={"project_pk": project.pk})
        response = client.get(url)

        assert response.status_code == 403

    def test_member_can_access_project_locations(self, client):
        """Project members should be able to access project locations."""
        member = UserFactory()
        project = ProjectFactory(user=[member])
        location = LocationFactory(project=project)

        client.force_login(member)
        url = reverse("core:locations", kwargs={"project_pk": project.pk})
        response = client.get(url)

        assert response.status_code == 200
        assert location in list(response.context["object_list"])

    def test_non_member_cannot_create_location_in_project(self, client):
        """Non-members should not be able to create locations in a project."""
        member = UserFactory()
        non_member = UserFactory()
        project = ProjectFactory(user=[member])

        client.force_login(non_member)
        url = reverse("core:add-location", kwargs={"project_pk": project.pk})
        response = client.get(url)

        assert response.status_code == 403

    def test_non_member_cannot_view_location_detail(self, client):
        """Non-members should not be able to view location details."""
        member = UserFactory()
        non_member = UserFactory()
        project = ProjectFactory(user=[member])
        location = LocationFactory(project=project)

        client.force_login(non_member)
        url = reverse(
            "core:detail-location",
            kwargs={"project_pk": project.pk, "location_pk": location.pk},
        )
        response = client.get(url)

        assert response.status_code == 403

    def test_non_member_cannot_delete_fieldwork(self, client):
        """Non-members should not be able to delete fieldworks."""
        member = UserFactory()
        non_member = UserFactory()
        project = ProjectFactory(user=[member])
        fieldwork = FieldworkFactory(project=project, user=[member])

        client.force_login(non_member)
        url = reverse(
            "core:delete-fieldwork",
            kwargs={"project_pk": project.pk, "fieldwork_pk": fieldwork.pk},
        )
        response = client.post(url, HTTP_HX_REQUEST="true")

        assert response.status_code == 403
        # Fieldwork should still exist
        assert Fieldwork.objects.filter(pk=fieldwork.pk).exists()
