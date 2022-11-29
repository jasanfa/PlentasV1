import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { ApiService } from 'src/app/services/api.service';
import { ConfigVariables } from 'src/app/services/configurationVariables';
import {ViewChild, ElementRef, AfterViewInit} from   '@angular/core';






@Component({
  selector: 'app-configuration2',
  templateUrl: './configuration2.component.html',
  styleUrls: ['./configuration2.component.css']
})
export class Configuration2Component implements OnInit {
  textminipregunta1 = "Minipregunta 1";
  textminipregunta2 = "Minipregunta 2";
  textminipregunta3 = "Minipregunta 3";
  textminipregunta4 = "Minipregunta 4";
  textminipregunta5 = "Minipregunta 5";

  textminirespuesta1 = "Minirespuesta 1";
  textminirespuesta2 = "Minirespuesta 2";
  textminirespuesta3 = "Minirespuesta 3";
  textminirespuesta4 = "Minirespuesta 4";
  textminirespuesta5 = "Minirespuesta 5";

  checkm1 = false;
  checkm2 = false;
  checkm3 = false;
  checkm4 = false;
  checkm5 = false;


  constructor(private variables: ConfigVariables) { }

  ngOnInit(): void {

    this.textminipregunta1 = this.variables.textminirespuesta1;
    this.textminipregunta2 = this.variables.textminirespuesta2;
    this.textminipregunta3 = this.variables.textminirespuesta3;
    this.textminipregunta4 = this.variables.textminirespuesta4;
    this.textminipregunta5 = this.variables.textminirespuesta5;

    this.textminirespuesta1 = this.variables.textminirespuesta1;
    this.textminirespuesta2 = this.variables.textminirespuesta2;
    this.textminirespuesta3 = this.variables.textminirespuesta3;
    this.textminirespuesta4 = this.variables.textminirespuesta4;
    this.textminirespuesta5 = this.variables.textminirespuesta5;

    this.checkm1 = this.variables.checkm1;
    this.checkm2 = this.variables.checkm2;
    this.checkm3 = this.variables.checkm3;
    this.checkm4 = this.variables.checkm4;
    this.checkm5 = this.variables.checkm5;

    
  }
  activarMinipregunta(type:any){
    
    if(type == 1){
      if(this.checkm1){
        this.textminipregunta1 = "Minipregunta 1";
        this.textminirespuesta1 = "Minirespuesta 1";        
      }else{
        this.textminipregunta1 = "";
        this.textminirespuesta1 = ""; 
      }
      this.checkm1 = !this.checkm1;
      this.checkm2 = false;
      this.checkm3 = false;
      this.checkm4 = false;
      this.checkm5 = false;

      this.textminipregunta2 = "Minipregunta 2";
      this.textminipregunta3 = "Minipregunta 3";
      this.textminipregunta4 = "Minipregunta 4";
      this.textminipregunta5 = "Minipregunta 5";

      this.textminirespuesta2 = "Minirespuesta 2";
      this.textminirespuesta3 = "Minirespuesta 3";
      this.textminirespuesta4 = "Minirespuesta 4";
      this.textminirespuesta5 = "Minirespuesta 5";

      
    }
    if(type == 2){
      if(this.checkm2){
        this.textminipregunta2 = "Minipregunta 2";
        this.textminirespuesta2 = "Minirespuesta 2";        
      }else{
        this.textminipregunta2 = "";
        this.textminirespuesta2 = ""; 
      }
      this.checkm2 = !this.checkm2;
      this.checkm3 = false;
      this.checkm4 = false;
      this.checkm5 = false;

      this.textminipregunta3 = "Minipregunta 3";
      this.textminipregunta4 = "Minipregunta 4";
      this.textminipregunta5 = "Minipregunta 5";

      this.textminirespuesta3 = "Minirespuesta 3";
      this.textminirespuesta4 = "Minirespuesta 4";
      this.textminirespuesta5 = "Minirespuesta 5";
    }
    if(type == 3){

      if(this.checkm3){
        this.textminipregunta3 = "Minipregunta 3";
        this.textminirespuesta3 = "Minirespuesta 3";        
      }else{
        this.textminipregunta3 = "";
        this.textminirespuesta3 = ""; 
      }
      this.checkm3 = !this.checkm3;
      this.checkm4 = false;
      this.checkm5 = false;

      this.textminipregunta4 = "Minipregunta 4";
      this.textminipregunta5 = "Minipregunta 5";

      this.textminirespuesta4 = "Minirespuesta 4";
      this.textminirespuesta5 = "Minirespuesta 5";
    }
    if(type == 4){

      if(this.checkm4){
        this.textminipregunta4 = "Minipregunta 4";
        this.textminirespuesta4 = "Minirespuesta 4";        
      }else{
        this.textminipregunta4 = "";
        this.textminirespuesta4 = ""; 
      }
      this.checkm4 = !this.checkm4;
      this.checkm5 = false;

      this.textminipregunta5 = "Minipregunta 5";
      this.textminirespuesta5 = "Minirespuesta 5";
    }
    if(type == 5){

      if(this.checkm5){
        this.textminipregunta5 = "Minipregunta 5";
        this.textminirespuesta5 = "Minirespuesta 5";        
      }else{
        this.textminipregunta5 = "";
        this.textminirespuesta5 = ""; 
      }
      this.checkm5 = !this.checkm5;
    }

    this.variables.textminipregunta1 = this.textminirespuesta1;
    this.variables.textminipregunta2 = this.textminirespuesta2;
    this.variables.textminipregunta3 = this.textminirespuesta3;
    this.variables.textminipregunta4 = this.textminirespuesta4;
    this.variables.textminipregunta5 = this.textminirespuesta5;

    this.variables.textminirespuesta1 = this.textminirespuesta1;
    this.variables.textminirespuesta2 = this.textminirespuesta2;
    this.variables.textminirespuesta3 = this.textminirespuesta3;
    this.variables.textminirespuesta4 = this.textminirespuesta4;
    this.variables.textminirespuesta5 = this.textminirespuesta5;

    this.variables.checkm1 = this.checkm1;
    this.variables.checkm2 = this.checkm2;
    this.variables.checkm3 = this.checkm3;
    this.variables.checkm4 = this.checkm4;
    this.variables.checkm5 = this.checkm5;

  }
  

}
