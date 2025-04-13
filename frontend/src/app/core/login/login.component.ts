import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpService } from '../../service/http.service';

interface LoginResponse {
  token: string;
  role: 'superAdmin' | 'collegeUser';
  userProfile: {
    username: string;
    email: string;
  };
}

@Component({
  selector: 'app-login',
  standalone: true,
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
  imports: [CommonModule, FormsModule]
})
export class LoginComponent {
  email = '';
  password = '';
  error = '';

  constructor(private http: HttpService, private router: Router) {}

  onSubmit(): void {
    if (!this.email || !this.password) {
      this.error = 'Both fields are required.';
      return;
    }

    this.http.post<LoginResponse>('api/login', { email: this.email, password: this.password }).subscribe({
      next: (res) => {
        localStorage.setItem('authToken', res.token);
        localStorage.setItem('role', res.role);
        localStorage.setItem('userProfile', JSON.stringify(res.userProfile));

        if (res.role === 'superAdmin') {
          this.router.navigate(['/admin/dashboard']);
        } else if (res.role === 'collegeUser') {
          this.router.navigate(['/admin/core/profile']);
        } else {
          this.router.navigate(['/login']);
        }
      },
      error: (err) => {
        console.error('Login error:', err);
        this.error = err.error?.error || 'Login failed';
      }
    });
  }
}
