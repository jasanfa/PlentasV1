import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  constructor(public http: HttpClient) {}

  post(jsonData: any) {
    return this.http.post<any>(environment.apiUrl, jsonData).toPromise();
  }
}
