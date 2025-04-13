import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { HttpService } from '../../service/http.service'; // Import HttpService

@Component({
  selector: 'app-change-password',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './change-password.component.html',
  styleUrls: ['./change-password.component.css']
})
export class ChangePasswordComponent {
  currentPassword = '';
  newPassword = '';
  confirmPassword = '';
  errorMessage = '';
  successMessage = '';

  constructor(private router: Router, private httpService: HttpService) {}

  changePassword(): void {
    // Check if all fields are filled
    if (!this.currentPassword || !this.newPassword || !this.confirmPassword) {
      this.errorMessage = 'Please fill in all fields.';
      this.successMessage = '';
      return;
    }

    // Check if the new password and confirm password match
    if (this.newPassword !== this.confirmPassword) {
      this.errorMessage = 'New password and confirm password do not match.';
      this.successMessage = '';
      return;
    }

    // Get the token from local storage
    const token = localStorage.getItem('authToken'); // Ensure you're using the same key as in the backend
    if (!token) {
      this.errorMessage = 'Unauthorized. Please log in.';
      return;
    }

    // Set up the request body
    const body = {
      currentPassword: this.currentPassword,
      newPassword: this.newPassword
    };

    // Call the HttpService to send the PUT request
    this.httpService.put('api/profile/change-password', body)
      .subscribe({
        next: (response: any) => {
          this.successMessage = response.message;
          this.errorMessage = '';
          setTimeout(() => {
            // Navigate to the profile page after 3 seconds
            this.router.navigate(['/profile']);
          }, 3000);
          // Clear the form fields after successful change
          this.currentPassword = '';
          this.newPassword = '';
          this.confirmPassword = '';
        },
        error: (error: any) => {
          // Handle error if the password change fails
          this.errorMessage = error.error.message || 'Failed to change password.';
          this.successMessage = '';
        }
      });
  }

  goBack(): void {
    // Navigate back to the profile page
    this.router.navigate(['/admin/core/profile']);
  }
}
