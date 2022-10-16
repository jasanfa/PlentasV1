import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { ApiService } from 'src/app/services/api.service';
import { ExperimentDataService } from 'src/app/services/experiment-data.service';
import { ExperimentDataServiceFeedback } from 'src/app/services/experiment-data.service2';
import { BufferEvaluation } from 'src/app/services/experiment-data.bufferEvaluacion';

@Component({
  selector: 'app-configuration',
  templateUrl: './configuration.component.html',
  styleUrls: ['./configuration.component.css'],
})
export class ConfigurationComponent implements OnInit {
  
  inputJsonFile: any = null;
  checkOrthography = false;
  checkSyntax = false;
  checkSemantic = false;
  public orthographyValue = 0.3;
  syntaxValue = 0.3;
  semanticValue = 0.4;

  inputData = '{';

  checkAll = false;
  checkStudentID = false; 
  checkStudentIDValue = "0-15"; 

  constructor(
    private toastr: ToastrService,
    private apiService: ApiService,
    public experimentDataService: ExperimentDataService,
    public experimentDataService2: ExperimentDataServiceFeedback,
    public bufferEvaluation: BufferEvaluation,
    private router: Router
  ) {}

  ngOnInit(): void {}

  async processInputData() {
    //Configure the json that will go to the api.py
    this.inputData = '{';
    this.inputData = this.inputData + '"filepath": ' + JSON.stringify(this.inputJsonFile)  + ',';
    if(this.checkSemantic){
      this.inputData = this.inputData + '"semanticPercentage": ' + this.semanticValue.toString()  + ',';
    }else{
      this.inputData = this.inputData + '"semanticPercentage": 0.0,';
    }
    if(this.checkSyntax){
      this.inputData = this.inputData + '"syntaxPercentage": ' + this.syntaxValue.toString() + ',';
    }else{
      this.inputData = this.inputData + '"syntaxPercentage": 0.0,';
    }
    if(this.checkOrthography){
      this.inputData = this.inputData + '"ortographyPercentage": ' + this.orthographyValue.toString() + ',';
    }else{
         this.inputData = this.inputData + '"ortographyPercentage": 0.0,';
    }

    if(this.checkAll){
      this.inputData = this.inputData + '"students": "All"';
    }else{
         this.inputData = this.inputData + '"students": "' + this.checkStudentIDValue + '"';
    }

    this.inputData = this.inputData + "}"








    if (this.inputData.trim().length == 0) {
      this.toastr.warning('Por favor introduzca los datos de entrada.');
      return;
    }

    let inputDataObject = null;

    try {
      inputDataObject = JSON.parse(this.inputData);
    } catch (error) {
      this.toastr.error(
        'El formato JSON de los datos de entrada es incorrecto.'
      );
      return;
    }

    try {
      const outputDataObject = await this.apiService.post(this.inputData);

      if (outputDataObject) {
        //this.experimentDataService.outputData = JSON.stringify(outputDataObject, null, 3);
        //this.evaluation = JSON.stringify(outputDataObject, null, 3);
        
        this.bufferEvaluation.outputData = JSON.stringify(outputDataObject, null, 3);
        this.experimentDataService.outputData = "{Prueba1}";
        this.experimentDataService2.outputData = "{Prueba2}";

        this.router.navigateByUrl('output');
      } else {
        this.toastr.error('No se han recibido datos de salida.');
      }
    } catch (error) {
      this.toastr.error(JSON.stringify(error), 'Error procesando datos', {
        disableTimeOut: true,
      });
    }
    
  }
}