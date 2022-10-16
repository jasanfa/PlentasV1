import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})

export class ConfigVariables {

  inputJsonFile: any = null;
  selectedFile:any = null;

  checkOrthography = false;
  checkSyntax = false;
  checkSemantic = false;

  orthographyValue = 0.3;
  syntaxValue = 0.3;
  semanticValue = 0.4;

  checkAll = false;
  checkStudentID = false; 
  checkStudentIDValue = "0-15"; 

  constructor() {}
  
}

