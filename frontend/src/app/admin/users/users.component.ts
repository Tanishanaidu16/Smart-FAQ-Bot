import { Component, OnInit, AfterViewInit, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { HttpService } from '../../service/http.service';
import $ from 'jquery';
import 'datatables.net';
import * as bootstrap from 'bootstrap';
 
@Component({
  selector: 'app-users',
  standalone: true,
  templateUrl: './users.component.html',
  styleUrls: ['./users.component.css'],
  imports: [CommonModule, FormsModule]
})
export class UsersComponent implements OnInit, AfterViewInit {
  dataSource: any[] = [];
  newUser = { name: '', email: '', password: '' };
  selectedUser: any = null;
  editUserData: any = { _id: '', name: '', email: '', password: '' };
  shouldInitializeTable = false;
 
  @ViewChild('usersTable') usersTable!: ElementRef;
 
  constructor(private httpService: HttpService) {}
 
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
 
  loadUsers(): void {
    // Destroy existing DataTable if present
    const table = $('#usersTable');
    if ($.fn.DataTable.isDataTable(table)) {
      table.DataTable().clear().destroy();
    }
 
    this.httpService.get<any[]>('api/college-users').subscribe({
      next: (users) => {
        this.dataSource = users;
        this.shouldInitializeTable = false;
 
        setTimeout(() => {
          this.shouldInitializeTable = true;
          setTimeout(() => {
            ($('#usersTable') as any).DataTable({
              columnDefs: [
                { targets: 2, orderable: false } // Disable sort on Actions
              ]
            });
          }, 0);
        }, 0);
      },
      error: (error) => {
        console.error('Error loading users:', error);
        alert('Failed to load users.');
      }
    });
  }
 
  createUser(): void {
    if (!this.newUser.name || !this.newUser.email || !this.newUser.password) {
      alert('Please fill all fields.');
      return;
    }
 
    this.httpService.post('api/college-users', this.newUser).subscribe({
      next: () => {
        this.newUser = { name: '', email: '', password: '' };
        this.loadUsers();
        alert('✅ User created successfully!');
        this.closeOffcanvas('createUserCanvas');
      },
      error: (error) => {
        console.error('Error creating user:', error);
        alert('Failed to create user.');
      }
    });
  }
 
  deleteUser(id: string): void {
    if (confirm('Are you sure you want to delete this user?')) {
      this.httpService.delete(`api/college-users/${id}`).subscribe({
        next: () => {
          this.loadUsers();
        },
        error: (error) => {
          console.error('Error deleting user:', error);
          alert('Failed to delete user.');
        }
      });
    }
  }
 
  viewUser(user: any): void {
    this.selectedUser = user;
    this.editUserData = { ...user, password: '' };
  }
 
  saveEdit(): void {
    const id = this.editUserData._id;
    this.httpService.put(`api/college-users/${id}`, this.editUserData).subscribe({
      next: () => {
        this.loadUsers();
        alert('✅ User updated successfully!');
        this.closeOffcanvas('editUserCanvas');
        this.cancelEdit();
      },
      error: (error) => {
        console.error('Error updating user:', error);
        alert('Failed to update user.');
      }
    });
  }
 
  cancelEdit(): void {
    this.editUserData = { _id: '', name: '', email: '', password: '' };
  }
 
  closeOffcanvas(id: string): void {
    const el = document.getElementById(id);
    if (el) {
      const bsOffcanvas = bootstrap.Offcanvas.getInstance(el) || new bootstrap.Offcanvas(el);
      bsOffcanvas.hide();
 
      const backdrops = document.querySelectorAll('.offcanvas-backdrop');
      backdrops.forEach(backdrop => backdrop.remove());
 
      document.body.classList.remove('offcanvas-backdrop', 'show');
      document.body.style.overflow = 'auto';
    }
  }
}
 