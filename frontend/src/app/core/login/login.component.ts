import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { Router } from '@angular/router';

interface UserProfile {
  username: string;
  email: string;
  // Add other profile properties if your backend returns them
}

interface LoginResponse {
  token: string;
  role: 'superAdmin' | 'collegeUser';
  userProfile: UserProfile; // Include userProfile in the response
}

@Component({
  selector: 'app-login',
  standalone: true,
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
  imports: [CommonModule, FormsModule, HttpClientModule],
})
export class LoginComponent {
  email = '';
  password = '';
  error = '';
  apiUrl: string = 'http://localhost:5000'; // Adjust if your API is on a different port or domain

  constructor(private http: HttpClient, private router: Router) {}

  onSubmit(): void {
    if (!this.email || !this.password) {
      this.error = 'Both fields are required.';
      return;
    }

    const loginUrl = `${this.apiUrl}/api/login`;
    console.log('Attempting login with:', { email: this.email, password: this.password });

    this.http.post<LoginResponse>(loginUrl, { email: this.email, password: this.password }).subscribe({
      next: (res) => {
        console.log('Login API Response:', res);
        localStorage.setItem('authToken', res.token); // Use 'authToken' consistently
        localStorage.setItem('role', res.role);
        localStorage.setItem('userProfile', JSON.stringify(res.userProfile)); // Store the profile
        console.log('Role stored in localStorage:', localStorage.getItem('role'));
        console.log('UserProfile stored in localStorage:', localStorage.getItem('userProfile'));

        if (res.role === 'superAdmin') {
          console.log('Navigating to admin dashboard.');
          this.router.navigate(['/admin/dashboard']);
        } else if (res.role === 'collegeUser') {
          console.log('Navigating to profile page.');
          this.router.navigate(['/admin/core/profile']); // Updated navigation path
        } else {
          console.log('Unknown role:', res.role, '. Redirecting to login.');
          this.router.navigate(['/login']); // Fallback
        }
      },
      error: (err) => {
        console.error('Login API Error:', err);
        this.error = err.error?.error || 'Login failed';
      },
    });
  }
}