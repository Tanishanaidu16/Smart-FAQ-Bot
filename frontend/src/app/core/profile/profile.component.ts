import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { HttpService } from '../../service/http.service';

interface UserProfile {
  username: string;
  email: string;
  college_name?: string;
  college_website?: string;
}

@Component({
  selector: 'app-profile',
  standalone: true,
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css'],
  imports: [CommonModule, FormsModule, RouterModule]
})
export class ProfileComponent implements OnInit {
  profile: UserProfile = { username: '', email: '', college_name: '', college_website: '' };
  isEditing = false;
  editProfile: UserProfile = { username: '', email: '', college_name: '', college_website: '' };
  updateError = '';
  updateSuccess = '';
  accessKey: string = '';
  showGenerateKeyButton: boolean = true;

  constructor(private router: Router, private http: HttpService) {}

  ngOnInit(): void {
    this.loadProfile();
  }

  loadProfile(): void {
    this.http.get<any>('api/profile').subscribe({
      next: (data) => {
        this.profile = {
          username: data.username || 'User',
          email: data.email,
          college_name: data.college_name || '',
          college_website: data.college_website || ''
        };
        this.editProfile = { ...this.profile };
        this.accessKey = data.access_key || '';
        this.showGenerateKeyButton = !this.accessKey;
        localStorage.setItem('userProfile', JSON.stringify(this.profile));
      },
      error: (err) => {
        console.error('Failed to load profile:', err);
        this.router.navigate(['/login']);
      }
    });
  }

  enableEditMode(): void {
    this.isEditing = true;
    this.editProfile = { ...this.profile };
  }

  disableEditMode(): void {
    this.isEditing = false;
    this.editProfile = { ...this.profile };
    this.updateError = '';
    this.updateSuccess = '';
  }

  saveProfile(): void {
    this.http.put('api/profile', this.editProfile).subscribe({
      next: (response) => {
        this.profile = { ...this.editProfile };
        localStorage.setItem('userProfile', JSON.stringify(this.profile));
        this.isEditing = false;
        this.updateSuccess = 'Profile updated successfully!';
        setTimeout(() => this.updateSuccess = '', 3000);
      },
      error: (err) => {
        console.error('Failed to update profile:', err);
        this.updateError = 'An error occurred while updating your profile.';
      }
    });
  }

  generateAccessKey(): void {
    this.http.post<any>('api/generate-access-key', {}).subscribe({
      next: (response) => {
        this.accessKey = response.access_key;
        this.showGenerateKeyButton = false;
      },
      error: (err) => {
        console.error('Failed to generate access key:', err);
      }
    });
  }

  logout(): void {
    localStorage.clear();
    this.router.navigate(['/login']);
  }
}
