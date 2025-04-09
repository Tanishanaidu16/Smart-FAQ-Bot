import { Component } from '@angular/core';
import { Router, RouterModule, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-super-admin-header',
  standalone: true,
  templateUrl: './super-admin-header.component.html',
  styleUrls: ['./super-admin-header.component.css'],
  imports: [RouterModule, CommonModule, RouterLinkActive]
})
export class SuperAdminHeaderComponent {
  constructor(public router: Router) {
    console.log('SuperAdminHeaderComponent initialized.'); // Console log in constructor
  }

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    this.router.navigate(['/login']);
  }
}