from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from profiles.models import TutorApplication, TutorProfile


class StaffDashboardTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user("staff", password="pass12345", is_staff=True)
        self.tutor_user = User.objects.create_user("pendingtutor", password="pass12345")
        self.tutor_profile = TutorProfile.objects.create(
            user=self.tutor_user,
            full_name="Pending Tutor",
            approval_status="pending",
        )
        self.application = TutorApplication.objects.create(user=self.tutor_user)

    def test_staff_dashboard_indicates_who_approves_tutors(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("staff_dashboard"))
        self.assertContains(response, "Staff/admin users approve tutor accounts here")
        self.assertContains(response, "Approve tutor")

    def test_staff_can_approve_tutor_application(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("review_tutor_application", args=[self.application.id, "approve"]))
        self.assertRedirects(response, reverse("staff_dashboard"))
        self.application.refresh_from_db()
        self.tutor_profile.refresh_from_db()
        self.assertEqual(self.application.status, "approved")
        self.assertEqual(self.tutor_profile.approval_status, "approved")
        self.assertEqual(self.application.reviewed_by, self.staff)
