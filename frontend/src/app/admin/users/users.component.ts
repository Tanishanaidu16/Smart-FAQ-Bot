import { Component, OnInit, AfterViewInit, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule, HttpHeaders } from '@angular/common/http';
import $ from 'jquery';
import 'datatables.net';
import * as bootstrap from 'bootstrap';

@Component({
  selector: 'app-users',
  standalone: true,
  templateUrl: './users.component.html',
  styleUrls: ['./users.component.css'],
  imports: [
    CommonModule,
    FormsModule,
  ]
})
export class UsersComponent implements OnInit, AfterViewInit {
  dataSource: any[] = [];
  newUser = { name: '', email: '', password: '' };
  selectedUser: any = null;
  editUserData: any = { _id: '', name: '', email: '', password: '' };

  @ViewChild('usersTable') usersTable!: ElementRef;

  // Retrieve the token from local storage
  private getToken(): string | null {
    return localStorage.getItem('authToken');
  }

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loadUsers();
  }

  ngAfterViewInit(): void {
    // Initialized in loadUsers after data is loaded
  }

  applyFilter(event: Event): void {
    const value = (event.target as HTMLInputElement).value.trim().toLowerCase();
    ($('#usersTable') as any).DataTable().search(value).draw();
  }
  shouldInitializeTable = false;

  loadUsers(): void {
    const token = this.getToken();
    if (!token) {
      console.error('Authentication token not found!');
      // Optionally redirect to login page
      return;
    }

    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    // Destroy existing DataTable if present
    const table = $('#usersTable');
    if ($.fn.DataTable.isDataTable(table)) {
      table.DataTable().clear().destroy();
    }

    // Fetch users
    this.http.get<any[]>('http://localhost:5000/api/college-users', { headers }).subscribe(
      users => {
        this.dataSource = users;

        // Step 1: Disable init temporarily
        this.shouldInitializeTable = false;

        // Step 2: Allow DOM to update via *ngIf + setTimeout
        setTimeout(() => {
          this.shouldInitializeTable = true;

          setTimeout(() => {
            ($('#usersTable') as any).DataTable({
              columnDefs: [
                { targets: 2, orderable: false } // Disable sort on Actions
              ]
            });
          }, 0); // Init after DOM render
        }, 0); // Delay to ensure ngIf reflects
      },
      error => {
        console.error('Error loading users:', error);
        if (error.status === 401) {
          alert('Unauthorized access. Please log in again.');
          // Optionally redirect to login page (e.g., this.router.navigate(['/login']));
        } else {
          alert('Failed to load users.');
        }
      }
    );
  }


  createUser(): void {
    const token = this.getToken();
    if (!token) {
      console.error('Authentication token not found!');
      return;
    }

    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    if (!this.newUser.name || !this.newUser.email || !this.newUser.password) {
      alert('Please fill all fields.');
      return;
    }

    this.http.post('http://localhost:5000/api/college-users', this.newUser, { headers }).subscribe(
      () => {
        this.newUser = { name: '', email: '', password: '' };
        this.loadUsers();
        alert('✅ User created successfully!');
        this.closeOffcanvas('createUserCanvas');
      },
      error => {
        console.error('Error creating user:', error);
        if (error.status === 401) {
          alert('Unauthorized access.');
        } else if (error.status === 400) {
          alert(error.error?.error || 'Failed to create user due to invalid data.');
        } else {
          alert('Failed to create user.');
        }
      }
    );
  }

  deleteUser(id: string): void {
    const token = this.getToken();
    if (!token) {
      console.error('Authentication token not found!');
      return;
    }

    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    if (confirm('Are you sure you want to delete this user?')) {
      this.http.delete(`http://localhost:5000/api/college-users/${id}`, { headers }).subscribe(
        () => {
          this.loadUsers();
        },
        error => {
          console.error('Error deleting user:', error);
          if (error.status === 401) {
            alert('Unauthorized access.');
          } else if (error.status === 404) {
            alert('User not found.');
          } else {
            alert('Failed to delete user.');
          }
        }
      );
    }
  }

  viewUser(user: any): void {
    this.selectedUser = user;
    this.editUserData = { ...user, password: '' };
  }

  saveEdit(): void {
    const token = this.getToken();
    if (!token) {
      console.error('Authentication token not found!');
      return;
    }

    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    const id = this.editUserData._id;
    this.http.put(`http://localhost:5000/api/college-users/${id}`, this.editUserData, { headers }).subscribe(
      () => {
        this.loadUsers();
        alert('✅ User updated successfully!');
        this.closeOffcanvas('editUserCanvas');
        this.cancelEdit();
      },
      error => {
        console.error('Error updating user:', error);
        if (error.status === 401) {
          alert('Unauthorized access.');
        } else if (error.status === 400) {
          alert(error.error?.error || 'Failed to update user due to invalid data.');
        } else if (error.status === 404) {
          alert('User not found.');
        } else {
          alert('Failed to update user.');
        }
      }
    );
  }

  cancelEdit(): void {
    this.editUserData = { _id: '', name: '', email: '', password: '' };
  }

  closeOffcanvas(id: string): void {
    const el = document.getElementById(id);
    if (el) {
      const bsOffcanvas = bootstrap.Offcanvas.getInstance(el) || new bootstrap.Offcanvas(el);
      bsOffcanvas.hide();

      // ⛏️ Remove backdrop manually if stuck
      const backdrops = document.querySelectorAll('.offcanvas-backdrop');
      backdrops.forEach(backdrop => backdrop.remove());

      document.body.classList.remove('offcanvas-backdrop', 'show');
      document.body.style.overflow = 'auto';
    }
  }
}