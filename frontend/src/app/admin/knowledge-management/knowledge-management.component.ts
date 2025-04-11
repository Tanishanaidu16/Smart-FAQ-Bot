import { Component, OnInit } from '@angular/core';
import { HttpService } from '../../service/http.service';
import { CommonModule } from '@angular/common';
 
@Component({
  selector: 'app-knowledge-management',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './knowledge-management.component.html'
})
export class KnowledgeManagementComponent implements OnInit {
  selectedFile: File | null = null;
  files: any[] = [];
 
  constructor(private httpService: HttpService) {}
 
  ngOnInit(): void {
    this.fetchFiles();
  }
 
  onFileChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input?.files?.length) {
      this.selectedFile = input.files[0];
    }
  }
 
  uploadPdf(event: Event): void {
    event.preventDefault();
 
    if (!this.selectedFile) {
      alert('Please select a PDF file');
      return;
    }
 
    const formData = new FormData();
    formData.append('file', this.selectedFile); // this key MUST be 'file'
 
    this.httpService.rawPost('api/upload', formData).subscribe({
      next: () => {
        alert('✅ PDF uploaded successfully');
        this.selectedFile = null;
        this.fetchFiles();
      },
      error: (err) => {
        console.error('Upload error:', err);
        alert('❌ Upload failed');
      }
    });
  }
 
 
  fetchFiles(): void {
    this.httpService.get<any[]>('api/files').subscribe({
      next: (res) => {
        this.files = res;
      },
      error: (err) => {
        console.error('Failed to load files:', err);
      }
    });
  }
 
  deletePdf(id: string): void {
    this.httpService.delete(`api/delete/${id}`).subscribe({
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
 
}