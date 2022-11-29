import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})

export class ConfigVariables {

  inputJsonFile: any = null;
  selectedFile:any = null;

  checkOrthography = false;
  checkSyntax = false;
  checkSemantic = true;

  orthographyValue = 0.0;
  syntaxValue = 0.0;
  semanticValue = 1.0;

  checkStudentRadio = "All"; 
  checkStudentIDValue = "0-15";
  
  isDataBeingProcessed = false;


  
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

  constructor() {}
  
}

