import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Experience, Project


class ProjectAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(username="owner", password="test-password", email="owner@example.com")
        self.visitor = User.objects.create_user(username="visitor", password="test-password")
        self.project = Project.objects.create(title="Portfolio", description="My website", tech_stack="Django")
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse("api:project-detail", args=[self.project.id])
        self.star_url = reverse("api:project-star", args=[self.project.id])
        self.payload = {"title":"New project", "description":"A useful app", "tech_stack":"Python", "project_url":"https://example.com/", "project_image_url":""}

    def test_public_list_search_detail_and_missing(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["id"], str(self.project.id))
        self.assertEqual(self.client.get(self.detail_url).status_code, 200)
        self.assertEqual(len(self.client.get(self.list_url, {"title":"PORT"}).data), 1)
        self.assertEqual(self.client.get(self.list_url, {"title":"missing"}).data, [])
        missing = reverse("api:project-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(missing).status_code, 404)

    def test_regular_users_cannot_mutate_and_owner_can(self):
        self.client.force_authenticate(user=self.visitor)
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.patch(self.detail_url, {"title":"Changed"}, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Project.objects.count(), 1)
        self.client.force_authenticate(user=self.owner)
        created = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(created.status_code, 201)
        detail = reverse("api:project-detail", args=[created.data["id"]])
        self.assertEqual(self.client.patch(detail, {"title":"Changed"}, format="json").status_code, 200)
        self.assertEqual(self.client.put(detail, self.payload, format="json").status_code, 200)
        self.assertEqual(self.client.delete(detail).status_code, 204)

    def test_validation_and_read_only_star_fields(self):
        self.client.force_authenticate(user=self.owner)
        for changes in ({"title":"   "}, {"title":"<b></b>"}, {"project_url":"javascript:alert(1)"}):
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, 400)
        response = self.client.post(self.list_url, {**self.payload,"star_count":99,"is_starred":True,"starred_by":[self.visitor.id]}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, 403)
        self.client.force_authenticate(user=self.visitor)
        self.assertTrue(self.client.post(self.star_url).data["is_starred"])
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_session_mutation_requires_csrf(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password="test-password")
        self.assertEqual(client.post(self.list_url, self.payload, format="json").status_code, 403)
        client.get(self.list_url, HTTP_ACCEPT="text/html")
        token = client.cookies["csrftoken"].value
        self.assertEqual(client.post(self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token).status_code, 201)


class ExperienceAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(username="owner", password="test-password", email="owner@example.com")
        self.visitor = User.objects.create_user(username="visitor", password="test-password", email="private@example.com")
        self.editor = User.objects.create_user(username="editor", password="test-password")
        self.editor.groups.add(Group.objects.create(name="Editor"))
        self.experience = Experience.objects.create(title="Research assistant", description="Built data tools", category="research")
        self.list_url = reverse("api:experience-list")
        self.detail_url = reverse("api:experience-detail", args=[self.experience.id])
        self.star_url = reverse("api:experience-star", args=[self.experience.id])
        self.payload = {"title":"New role", "description":"A role", "category":"internship", "thumbnail":"https://example.com/image.jpg", "ended_at":None}

    def test_public_list_detail_search_and_safe_fields(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["id"], str(self.experience.id))
        self.assertIn("star_count", response.data[0])
        self.assertIn("is_starred", response.data[0])
        self.assertNotIn("starred_by", response.data[0])
        self.assertNotIn("email", response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, 200)
        self.assertEqual(len(self.client.get(self.list_url, {"title":"RESEARCH"}).data), 1)
        self.assertEqual(self.client.get(self.list_url, {"title":"missing"}).data, [])

    def test_guest_and_regular_user_cannot_write_but_can_star(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title":"Changed"}, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Experience.objects.count(), 1)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.client.post(self.star_url)
        self.assertEqual(self.experience.starred_by.count(), 0)

    def test_editor_can_patch_but_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)
        self.assertEqual(self.client.patch(self.detail_url, {"title":"Edited"}, format="json").status_code, 200)
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Edited")
        self.assertEqual(Experience.objects.count(), 1)

    def test_owner_can_create_update_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, 201)
        detail = reverse("api:experience-detail", args=[response.data["id"]])
        self.assertEqual(self.client.patch(detail, {"title":"Changed"}, format="json").status_code, 200)
        self.assertEqual(self.client.put(detail, {**self.payload,"title":"Replacement"}, format="json").status_code, 200)
        self.assertEqual(self.client.delete(detail).status_code, 204)
        self.assertFalse(Experience.objects.filter(pk=response.data["id"]).exists())

    def test_validation_and_missing_detail(self):
        self.client.force_authenticate(user=self.owner)
        for changes in ({"title":"   "}, {"title":"<b></b>"}, {"category":"invalid"}, {"thumbnail":"javascript:alert(1)"}):
            self.assertEqual(self.client.post(self.list_url, {**self.payload, **changes}, format="json").status_code, 400)
        self.assertEqual(Experience.objects.count(), 1)
        missing = reverse("api:experience-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(missing).status_code, 404)

    def test_session_write_rejects_missing_csrf_token(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        self.assertEqual(client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(Experience.objects.count(), 1)
        client.get(reverse("main:show_experience"))
        token = client.cookies["csrftoken"].value
        self.assertEqual(client.post(self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token).status_code, 201)
