import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { ApiService } from 'src/app/services/api.service';
import { ExperimentDataService } from 'src/app/services/experiment-data.service';
import { ExperimentDataServiceFeedback } from 'src/app/services/experiment-data.service2';
import { BufferEvaluation } from 'src/app/services/experiment-data.bufferEvaluacion';
import { ConfigVariables } from 'src/app/services/configurationVariables';

@Component({
  selector: 'app-configuration',
  templateUrl: './configuration.component.html',
  styleUrls: ['./configuration.component.css'],
})

export class ConfigurationComponent implements OnInit {
  
  inputJsonFile:any = null;
  public selectedFile:any = null;

  checkOrthography = false;
  checkSyntax = false;
  checkSemantic = true;
  public orthographyValue = 0.0;
  syntaxValue = 0.0;
  semanticValue = 1.0;

  inputData = '{';

  checkStudentRadio = "All"
  checkStudentIDValue = "Ej: 0-15, 18-20";
  
  isDataBeingProcessed = false;
  value = 0;

  studentsSelection = ""


  constructor(
    private toastr: ToastrService,
    private apiService: ApiService,
    public experimentDataService: ExperimentDataService,
    public experimentDataService2: ExperimentDataServiceFeedback,
    public bufferEvaluation: BufferEvaluation,
    private router: Router,
    private variables: ConfigVariables
  ) {}

  ngOnInit(): void {
    this.inputJsonFile = this.variables.inputJsonFile;
    //this.selectedFile = this.variables.selectedFile;
  
    this.checkOrthography = this.variables.checkOrthography;
    this.checkSyntax = this.variables.checkSyntax;
    this.checkSemantic = this.variables.checkSemantic;
    this.orthographyValue = this.variables.orthographyValue;
    this.syntaxValue = this.variables.syntaxValue;
    this.semanticValue = this.variables.semanticValue;
   
    this.checkStudentRadio = this.variables.checkStudentRadio;

    this.checkStudentIDValue = this.variables.checkStudentIDValue; 

    this.isDataBeingProcessed = this.variables.isDataBeingProcessed;

    
    

  }

	onFileSelected(event:any) {
		if (event.target.files.length == 0) {
			this.selectedFile = null;
			return;
		}

    const file:File = event.target.files[0];

    if (file) {
        this.selectedFile = file;
    }
  }
  
  changeRubricWeights(type:any){

    
    if(type == 1){
      this.orthographyValue = 0.0;
      
    }
    if(type == 2){
      this.syntaxValue = 0.0;
    }
    if(type == 3){

      this.semanticValue = 0.0;
    }

  }


  
  openPopup(){
    let popup = document.getElementById("popup");
    popup?.classList.add("open-popup")

  }

  closePopup(){
    let popup = document.getElementById("popup");
    popup?.classList.remove("open-popup")
  }


  async processInputData() {
    this.value = parseFloat(this.orthographyValue.toString()) + parseFloat(this.syntaxValue.toString()) + parseFloat(this.semanticValue.toString());

    if (!this.variables.checkm1 || (this.variables.checkm1 && this.variables.textminipregunta1== "") || (this.variables.checkm1 && this.variables.textminirespuesta1 == "")){
      this.toastr.error('Introduzca al menos una minipregunta y una minirespuesta');
      return
    }

    if (this.value != 1.0){
      this.toastr.error('El valor de los pesos de la rubrica debe sumar 1');
      return
    }

    if (this.checkStudentRadio != "All" && this.checkStudentIDValue == ""){
      this.toastr.error('No se ha especificado ningún rango de estudiantes');
      return
    }

 

    this.isDataBeingProcessed = true
    
    //Configure the json that will go to the api.py
    this.inputData = '{';
    this.inputData = this.inputData + '"filepath": ' + JSON.stringify(this.inputJsonFile)  + ',';

    if(this.variables.checkm1){
      this.inputData = this.inputData + '"minip1": ' + JSON.stringify(this.variables.textminipregunta1)  + ',';
      this.inputData = this.inputData + '"minir1": ' + JSON.stringify(this.variables.textminirespuesta1)  + ',';
    }

    if(this.variables.checkm2){
      this.inputData = this.inputData + '"minip2": ' + JSON.stringify(this.variables.textminipregunta2)  + ',';
      this.inputData = this.inputData + '"minir2": ' + JSON.stringify(this.variables.textminirespuesta2)  + ',';
    }

    if(this.variables.checkm3){
      this.inputData = this.inputData + '"minip3": ' + JSON.stringify(this.variables.textminipregunta3)  + ',';
      this.inputData = this.inputData + '"minir3": ' + JSON.stringify(this.variables.textminirespuesta3)  + ',';
    }

    if(this.variables.checkm4){
      this.inputData = this.inputData + '"minip4": ' + JSON.stringify(this.variables.textminipregunta4)  + ',';
      this.inputData = this.inputData + '"minir4": ' + JSON.stringify(this.variables.textminirespuesta4)  + ',';
    }

    if(this.variables.checkm5){
      this.inputData = this.inputData + '"minip5": ' + JSON.stringify(this.variables.textminipregunta5)  + ',';
      this.inputData = this.inputData + '"minir5": ' + JSON.stringify(this.variables.textminirespuesta5)  + ',';
    }  
    
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

    
    if(this.checkStudentRadio == "All"){
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
      //const outputDataObject = await this.apiService.post(this.inputData);
      if (this.inputJsonFile != "") {
            
        const formData = new FormData();
        try{
          formData.append("zipFile", this.selectedFile);
        }catch{
          formData.append("zipFile", "");
        }        
  
        formData.append("configuration", this.inputData); // donde this.inputData es un JSON (string) con los datos de configuracion
  
        const outputDataObject = await this.apiService.post(formData);
        
        if (outputDataObject) {
          this.isDataBeingProcessed = false;
          //this.experimentDataService.outputData = JSON.stringify(outputDataObject, null, 3);
          //this.evaluation = JSON.stringify(outputDataObject, null, 3);
          
          this.bufferEvaluation.outputData = JSON.stringify(outputDataObject, null, 3);
          //this.experimentDataService.outputData = "{Prueba1}";
          //this.experimentDataService2.outputData = "{Prueba2}";

          this.router.navigateByUrl('output');
        } else {
          this.toastr.error('No se han recibido datos de salida.');
        }
        
  
      }
  

      } catch (error) {
        this.toastr.error(JSON.stringify(error), 'Error procesando datos', {
          disableTimeOut: true,
        });
        this.isDataBeingProcessed = false;
      }

    this.variables.inputJsonFile = this.inputJsonFile;
    //this.variables.selectedFile = this.selectedFile;
  
    this.variables.checkOrthography = this.checkOrthography;
    this.variables.checkSyntax = this.checkSyntax;
    this.variables.checkSemantic = this.checkSemantic;
    this.variables.orthographyValue = this.orthographyValue;
    this.variables.syntaxValue = this.syntaxValue;
    this.variables.semanticValue = this.semanticValue;
    
    this.variables.checkStudentRadio = this.checkStudentRadio;
    this.variables.checkStudentIDValue = this.checkStudentIDValue;
    
    this.variables.isDataBeingProcessed = this.isDataBeingProcessed;   
    
    
  }
  

}

