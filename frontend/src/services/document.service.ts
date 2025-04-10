import { Injectable } from '@angular/core';
import { of, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class DocumentService {
  private documents: { name: string }[] = [];

  uploadDocument(file: File): Observable<void> {
    this.documents.push({ name: file.name });
    return of();
  }

  deleteDocument(name: string): Observable<void> {
    this.documents = this.documents.filter(doc => doc.name !== name);
    return of();
  }

  getDocuments(): Observable<{ name: string }[]> {
    return of(this.documents);
  }
}
 