import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FooterComponent } from './footer/footer.component'; // Adjust the path if your FooterComponent is in a different folder
import { SuperAdminHeaderComponent } from './super-admin-header/super-admin-header.component'; // Assuming this is your folder structure

@Component({
  selector: 'app-layout',
  standalone: true,
  templateUrl: './layout.component.html',
  styleUrls: ['./layout.component.css'],
  imports: [CommonModule, RouterOutlet, SuperAdminHeaderComponent,FooterComponent],
})
export class LayoutComponent implements OnInit {
  userRole: string | null = null;

  constructor() {}

  ngOnInit(): void {
    this.userRole = localStorage.getItem('role');
    console.log('LayoutComponent initialized. User role from localStorage:', this.userRole); // Console log in ngOnInit
  }
}