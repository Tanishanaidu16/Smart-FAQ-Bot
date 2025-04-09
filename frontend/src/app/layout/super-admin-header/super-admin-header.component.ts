import { Component, OnInit } from '@angular/core';
import { Router, RouterModule, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-super-admin-header',
  standalone: true,
  templateUrl: './super-admin-header.component.html',
  styleUrls: ['./super-admin-header.component.css'],
  imports: [RouterModule, CommonModule, RouterLinkActive]
})
export class SuperAdminHeaderComponent implements OnInit {
  userRole: string | null = null;

  constructor(public router: Router) {
    console.log('SuperAdminHeaderComponent initialized.');
  }

  ngOnInit(): void {
    this.userRole = localStorage.getItem('role');
    console.log('User Role:', this.userRole);
  }

  logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('role');
    this.router.navigate(['/login']);
  }
}