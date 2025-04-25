import { Component, OnInit } from '@angular/core';
import { HttpService } from '../../service/http.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms'; // ✅ Add this
@Component({
  selector: 'app-knowledge-management',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './knowledge-management.component.html',
  styleUrls: ['./knowledge-management.component.css'],
})
export class KnowledgeManagementComponent implements OnInit {
  selectedFile: File | null = null;
  pdfDescription: string = '';
  url: string = '';
  urlDescription: string = '';
  files: any[] = [];
  urls: any[] = [];
  activeTab: string = 'pdf';
 
  constructor(private httpService: HttpService) {}
 
  ngOnInit(): void {
    this.fetchFiles();
    this.fetchUrls();
  }
 
  setTab(tab: string) {
    this.activeTab = tab;
  }
 
  onFileChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input?.files?.length) {
      this.selectedFile = input.files[0];
    }
  }
 
  uploadPdf(event: Event): void {
    event.preventDefault();
    if (!this.selectedFile || !this.pdfDescription) {
      alert('📄 Please select a file and enter a description');
      return;
    }
 
    const formData = new FormData();
    formData.append('file', this.selectedFile);
    formData.append('description', this.pdfDescription);
 
    this.httpService.rawPost('api/upload-pdf', formData).subscribe({
      next: () => {
        alert('✅ PDF uploaded successfully');
        this.selectedFile = null;
        this.pdfDescription = '';
        this.fetchFiles();
      },
      error: (err) => {
        console.error('Upload error:', err);
        alert('❌ Upload failed');
      }
    });
  }
 
  fetchFiles(): void {
    this.httpService.get<any[]>('api/pdfs').subscribe({
      next: (res) => this.files = res,
      error: (err) => console.error('Failed to load files:', err)
    });
  }
 
  deletePdf(id: string): void {
    this.httpService.delete(`api/delete-pdf/${id}`).subscribe({
      next: () => {
        this.files = this.files.filter(file => file.id !== id);
        alert('🗑️ File deleted successfully!');
      },
      error: (err) => {
        console.error('Delete error:', err);
        alert('❌ Failed to delete file.');
      }
    });
  }
 
  addUrl(): void {
    if (!this.url || !this.urlDescription) {
      alert('🌐 Enter both URL and description');
      return;
    }
 
    this.httpService.post('api/add-url', {
      url: this.url,
      description: this.urlDescription
    }).subscribe({
      next: () => {
        alert('✅ URL added successfully');
        this.url = '';
        this.urlDescription = '';
        this.fetchUrls();
      },
      error: (err) => {
        console.error('Add URL error:', err);
        alert('❌ Failed to add URL');
      }
    });
  }
 
  fetchUrls(): void {
    this.httpService.get<any[]>('api/urls').subscribe({
      next: (res) => this.urls = res,
      error: (err) => console.error('Failed to load URLs:', err)
    });
  }
 
  deleteUrl(id: string): void {
    this.httpService.delete(`api/delete-url/${id}`).subscribe({
      next: () => {
        this.urls = this.urls.filter(url => url.id !== id);
        alert('🗑️ URL deleted successfully!');
      },
      error: (err) => {
        console.error('Delete URL error:', err);
        alert('❌ Failed to delete URL.');
      }
    });
  }
}