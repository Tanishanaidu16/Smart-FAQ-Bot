import { Injectable, inject, DestroyRef } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { timeout } from 'rxjs';
 
@Injectable({
  providedIn: 'root'
})
export class HttpService {
  private defaultTimeout = 900000;
  destroyRef = inject(DestroyRef);
  baseUrl = 'http://127.0.0.1:5000';
 
  constructor(private readonly httpClient: HttpClient) {}
 
  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('authToken');
    let headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    if (token) {
      headers = headers.set('Authorization', `Bearer ${token}`);
    }
    return headers;
  }
 
  get<T>(url: string) {
    return this.httpClient
      .get<T>(`${this.baseUrl}/${url}`, { headers: this.getHeaders() })
      .pipe(timeout(this.defaultTimeout), takeUntilDestroyed(this.destroyRef));
  }
 
  post<T>(url: string, body: any) {
    return this.httpClient
      .post<T>(`${this.baseUrl}/${url}`, body, { headers: this.getHeaders() })
      .pipe(timeout(this.defaultTimeout), takeUntilDestroyed(this.destroyRef));
  }
 
  put<T>(url: string, body: any) {
    return this.httpClient
      .put<T>(`${this.baseUrl}/${url}`, body, { headers: this.getHeaders() })
      .pipe(timeout(this.defaultTimeout), takeUntilDestroyed(this.destroyRef));
  }
 
  patch<T>(url: string, body: any) {
    return this.httpClient
      .patch<T>(`${this.baseUrl}/${url}`, body, { headers: this.getHeaders() })
      .pipe(timeout(this.defaultTimeout), takeUntilDestroyed(this.destroyRef));
  }
 
  delete<T>(url: string) {
    return this.httpClient
      .delete<T>(`${this.baseUrl}/${url}`, { headers: this.getHeaders() })
      .pipe(timeout(this.defaultTimeout), takeUntilDestroyed(this.destroyRef));
  }
  rawPost<T>(url: string, body: any) {
    const token = localStorage.getItem('authToken');
 
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
 
    return this.httpClient
      .post<T>(`${this.baseUrl}/${url}`, body, {
        headers,
      })
      .pipe(timeout(this.defaultTimeout), takeUntilDestroyed(this.destroyRef));
  }
}
 