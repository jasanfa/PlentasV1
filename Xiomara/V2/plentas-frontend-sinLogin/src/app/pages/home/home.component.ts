import { Component, OnInit } from '@angular/core';
import { ToastrService } from 'ngx-toastr';
import { ApiService } from 'src/app/services/api.service';
import { ConfigVariables } from 'src/app/services/configurationVariables';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
})
export class HomeComponent implements OnInit {

  prueba:any = this.variables.inputJsonFile;
 
  constructor(private toastr: ToastrService, private apiService: ApiService, private variables: ConfigVariables) {}

  ngOnInit(): void {}
 
}
//<div *ngIf="prueba != null" class="home-button" routerLink="/output">