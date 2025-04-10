import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DocumentService } from '../../../services/document.service';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-knowledge-management',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './knowledge-management.component.html',
  styleUrls: ['./knowledge-management.component.css']
})
export class KnowledgeManagementComponent {
  selectedFile: File | null = null;
  files: any[] = [];

  constructor(private http: HttpClient) {
    this.loadFiles();
  }

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
  }

  uploadFile() {
    if (!this.selectedFile) return;

    const formData = new FormData();
    formData.append('file', this.selectedFile);

    this.http.post('http://localhost:5000/upload', formData).subscribe({
      next: () => {
        this.selectedFile = null;
        this.loadFiles();
      },
      error: err => alert('Upload failed: ' + (err.error?.error || err.message))
    });
  }

  loadFiles() {
    this.http.get<any[]>('http://localhost:5000/files').subscribe(data => {
      this.files = data;
    });
  }

  downloadFile(fileId: string, filename: string) {
    this.http.get(`http://localhost:5000/download/${fileId}`, { responseType: 'blob' })
      .subscribe(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        window.URL.revokeObjectURL(url);
      });
  }

  deleteFile(fileId: string) {
    this.http.delete(`http://localhost:5000/delete/${fileId}`).subscribe(() => {
      this.loadFiles();
    });
  }
}
