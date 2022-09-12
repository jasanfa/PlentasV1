import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  constructor(public http: HttpClient) {}

  post(jsonData: string) {
    return this.http.post<any>(environment.apiUrl, jsonData, {
      headers: new HttpHeaders({ 'Content-Type': 'application/json' }),
    }).toPromise();
  }
}
