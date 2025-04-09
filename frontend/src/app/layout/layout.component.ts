import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { SuperAdminHeaderComponent } from '../super-admin-header/super-admin-header.component';// Assuming this is your folder structure
import { CollegeHeaderComponent } from '../college-header/college-header.component'; // Assuming this is your folder structure
import { FooterComponent } from '../footer/footer.component'; // Adjust the path if your FooterComponent is in a different folder

@Component({
  selector: 'app-layout',
  standalone: true,
  templateUrl: './layout.component.html',
  styleUrls: ['./layout.component.css'],
  imports: [CommonModule, RouterOutlet, SuperAdminHeaderComponent, CollegeHeaderComponent,FooterComponent],
})
export class LayoutComponent implements OnInit {
  userRole: string | null = null;

  constructor() {}

  ngOnInit(): void {
    this.userRole = localStorage.getItem('role');
    console.log('LayoutComponent initialized. User role from localStorage:', this.userRole); // Console log in ngOnInit
  }
}