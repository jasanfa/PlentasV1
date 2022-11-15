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

  checkAll = true;
  checkStudentID = false; 
  checkStudentIDValue = "0-15";
  
  isDataBeingProcessed = false;

  constructor() {}
  
}

