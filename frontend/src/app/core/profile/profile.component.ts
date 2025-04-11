import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { HttpService } from '../../service/http.service';
 
interface UserProfile {
  username: string;
  email: string;
}
 
@Component({
  selector: 'app-profile',
  standalone: true,
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css'],
  imports: [CommonModule, FormsModule, RouterModule]
})
export class ProfileComponent implements OnInit {
  profile: UserProfile = { username: '', email: '' };
  isEditing = false;
  editProfile: UserProfile = { username: '', email: '' };
  updateError = '';
  updateSuccess = '';
 
  constructor(private router: Router, private http: HttpService) {}
 
  ngOnInit(): void {
    this.loadProfile();
  }
 
  loadProfile(): void {
    this.http.get<UserProfile>('api/profile').subscribe({
      next: (data) => {
        this.profile = {
          username: data.username || 'User',
          email: data.email
        };
        this.editProfile = { ...this.profile };
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
    this.profile = { ...this.editProfile };
    localStorage.setItem('userProfile', JSON.stringify(this.profile));
    this.isEditing = false;
    this.updateSuccess = 'Profile updated successfully!';
    setTimeout(() => this.updateSuccess = '', 3000);
  }
 
  logout(): void {
    localStorage.clear();
    this.router.navigate(['/login']);
  }
}
 