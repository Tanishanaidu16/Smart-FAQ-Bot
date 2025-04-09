import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { Router } from '@angular/router';

interface LoginResponse {
  token: string;
  role: 'superAdmin' | 'collegeUser';
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
  apiUrl: string = 'http://localhost:5000'; // Directly hardcoding the base API URL

  constructor(private http: HttpClient, private router: Router) {}

  onSubmit(): void {
    if (!this.email || !this.password) {
      this.error = 'Both fields are required.';
      return;
    }

    const loginUrl = `${this.apiUrl}/api/login`;

    this.http.post<LoginResponse>(loginUrl, { email: this.email, password: this.password }).subscribe({
      next: (res) => {
        localStorage.setItem('token', res.token);
        localStorage.setItem('role', res.role);
        console.log('Login successful! Role stored in localStorage:', localStorage.getItem('role')); // Console log after storing role
        alert('Login successful!');
        if (res.role === 'superAdmin') {
          this.router.navigate(['/admin/dashboard']);
        } else if (res.role === 'collegeUser') {
          this.router.navigate(['/core/profile']);
        }
      },
      error: (err) => {
        this.error = err.error?.error || 'Login failed';
      },
    });
  }
}