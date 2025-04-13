import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { HttpService } from '../../service/http.service';

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
    // Validate fields
    if (!this.currentPassword || !this.newPassword || !this.confirmPassword) {
      this.errorMessage = 'Please fill in all fields.';
      this.successMessage = '';
      return;
    }

    // Match new and confirm password
    if (this.newPassword !== this.confirmPassword) {
      this.errorMessage = 'New password and confirm password do not match.';
      this.successMessage = '';
      return;
    }

    // Ensure user is authenticated
    const token = localStorage.getItem('authToken');
    if (!token) {
      this.errorMessage = 'Unauthorized. Please log in.';
      return;
    }

    const body = {
      currentPassword: this.currentPassword,
      newPassword: this.newPassword
    };

    this.httpService.put('api/profile/change-password', body).subscribe({
      next: (response: any) => {
        this.successMessage = response.message;
        this.errorMessage = '';

        // ✅ Show alert immediately
        alert('Password updated successfully!');

        // ✅ Redirect to profile page
        this.router.navigate(['admin/core/profile']);

        // Clear fields
        this.currentPassword = '';
        this.newPassword = '';
        this.confirmPassword = '';
      },
      error: (error: any) => {
        this.errorMessage = error.error.message || 'Failed to change password.';
        this.successMessage = '';
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/admin/core/profile']);
  }
}
