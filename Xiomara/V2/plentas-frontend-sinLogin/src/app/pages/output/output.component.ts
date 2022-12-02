import { Component, OnInit } from '@angular/core';
import { ToastrService } from 'ngx-toastr';
import { ExperimentDataService } from 'src/app/services/experiment-data.service';
import { ExperimentDataServiceFeedback } from 'src/app/services/experiment-data.service2';
import { BufferEvaluation } from 'src/app/services/experiment-data.bufferEvaluacion';


@Component({
  selector: 'app-output',
  templateUrl: './output.component.html',
  styleUrls: ['./output.component.css']
})
export class OutputComponent implements OnInit {

  evaluation:any;
  ID = 0;
  ID_show = 1
  ID_show_old = 0
  NumberPagesTable = 0

  numberStudents = 0

  stdnt_ID_1 = "Pepe";
  stdnt_ID_2 = "Pepe";
  stdnt_ID_3 = "Juan";
  stdnt_ID_4 = "Pepe";
  stdnt_ID_5 = "Jeronimo";
  stdnt_ID_6 = "Pepe";
  stdnt_ID_7 = "Pepe";
  stdnt_ID_8 = "Pepe";
  stdnt_ID_9 = "Pepe";
  stdnt_ID_10 = "Pepe";

  spacy_1 = "";
  spacy_2 = "";
  spacy_3 = "";
  spacy_4 = "";
  spacy_5 = "";
  spacy_6 = "";
  spacy_7 = "";
  spacy_8 = "";
  spacy_9 = "";
  spacy_10 = "";

  bert_1 = "";
  bert_2 = "";
  bert_3 = "";
  bert_4 = "";
  bert_5 = "";
  bert_6 = "";
  bert_7 = "";
  bert_8 = "";
  bert_9 = "";
  bert_10 = "";

  bert_sintaxis = 0;
  bert_ortografia = 0;
  bert_semantica = 0;

  spacy_sintaxis = 0;
  spacy_ortografia = 0;
  spacy_semantica = 0;
  

  constructor(public experimentDataService: ExperimentDataService, public experimentDataService2: ExperimentDataServiceFeedback, public bufferEvaluation: BufferEvaluation, private toastr: ToastrService) { }

  ngOnInit(): void {
    this.evaluation = this.bufferEvaluation.outputData;
    this.numberStudents = JSON.parse(this.evaluation).length;
    this.updateTable();
    this.ID_show = this.ID + 1;   


  }

  showFeedback(tableIndx:any){
    //document.write("blabla");
    var fdbckIndx = tableIndx + this.ID*10;
    var Plentas = JSON.parse(JSON.stringify(JSON.parse(this.evaluation)[fdbckIndx]));     
    this.experimentDataService2.outputData = JSON.parse(JSON.stringify(Plentas[fdbckIndx.toString()]["Feedback"]));

    //Esto es el desglose de la rubrica
    this.bert_ortografia = Number(JSON.parse(JSON.stringify(Plentas[fdbckIndx.toString()]["NotaOrtografiaBert"])).toFixed(2));
    this.bert_sintaxis = Number(JSON.parse(JSON.stringify(Plentas[fdbckIndx.toString()]["NotaSintaxisBert"])).toFixed(2));
    this.bert_semantica = Number(JSON.parse(JSON.stringify(Plentas[fdbckIndx.toString()]["NotaSemanticaBert"])).toFixed(2));

    this.spacy_ortografia = Number(JSON.parse(JSON.stringify(Plentas[fdbckIndx.toString()]["NotaOrtografiaSpacy"])).toFixed(2));
    this.spacy_sintaxis = Number(JSON.parse(JSON.stringify(Plentas[fdbckIndx.toString()]["NotaSintaxisSpacy"])).toFixed(2));
    this.spacy_semantica = Number(JSON.parse(JSON.stringify(Plentas[fdbckIndx.toString()]["NotaSemanticaSpacy"])).toFixed(2));


    
  }


  updateTable(){
    this.ID = this.ID_show - 1;
    if (this.ID >= this.NumberPagesTable){
      this.ID = 0;
      this.ID_show = 1;
    }
    var division = this.numberStudents / 10;
    var rest = this.numberStudents % 10;
    if (rest == 0){
      this.NumberPagesTable = Math.trunc(division);
    }else{
      this.NumberPagesTable = Math.trunc(division) + 1;
    }
     
    
    var indx = 0 + this.ID*10;
    //document.write(JSON.stringify(this.ID))

    if (indx >= this.numberStudents) {
      this.stdnt_ID_1 = "- - - - -";
      this.spacy_1 = "- - -";
      this.bert_1 = "- - -";
    }else{
      var Plentas = JSON.parse(JSON.stringify(JSON.parse(this.evaluation)[0 + this.ID*10]));
      this.stdnt_ID_1 = JSON.stringify(Plentas[indx.toString()]["ID"]);
      this.spacy_1 = JSON.stringify(Plentas[indx.toString()]["NotaSpacy"]);
      this.bert_1 = JSON.stringify(Plentas[indx.toString()]["NotaBert"]);
    } 

    
    var indx = 1 + this.ID*10;
    //document.write(JSON.stringify(this.ID))

    if (indx >= this.numberStudents) {
      this.stdnt_ID_2 = "- - - - -";
      this.spacy_2 = "- - -";
      this.bert_2 = "- - -";
    }else{
      var Plentas = JSON.parse(JSON.stringify(JSON.parse(this.evaluation)[1 + this.ID*10]));
      this.stdnt_ID_2 = JSON.stringify(Plentas[indx.toString()]["ID"]);
      this.spacy_2 = JSON.stringify(Plentas[indx.toString()]["NotaSpacy"]);
      this.bert_2 = JSON.stringify(Plentas[indx.toString()]["NotaBert"]);

    }

    var indx = 2 + this.ID*10;
    //document.write(JSON.stringify(this.ID))


    if (indx >= this.numberStudents) {
      this.stdnt_ID_3 = "- - - - -";
      this.spacy_3 = "- - -";
      this.bert_3 = "- - -";
    }else{
      var Plentas = JSON.parse(JSON.stringify(JSON.parse(this.evaluation)[2 + this.ID*10])); 
      this.stdnt_ID_3 = JSON.stringify(Plentas[indx.toString()]["ID"]);
      this.spacy_3 = JSON.stringify(Plentas[indx.toString()]["NotaSpacy"]);
      this.bert_3 = JSON.stringify(Plentas[indx.toString()]["NotaBert"]);
    }

    
    var indx = 3 + this.ID*10;

    if (indx >= this.numberStudents) {
      this.stdnt_ID_4 = "- - - - -";
      this.spacy_4 = "- - -";
      this.bert_4 = "- - -";
      
    }else{
      var Plentas = JSON.parse(JSON.stringify(JSON.parse(this.evaluation)[3 + this.ID*10])); 
      this.stdnt_ID_4 = JSON.stringify(Plentas[indx.toString()]["ID"]);
      this.spacy_4 = JSON.stringify(Plentas[indx.toString()]["NotaSpacy"]);
      this.bert_4 = JSON.stringify(Plentas[indx.toString()]["NotaBert"]);
    }

     
    var indx = 4 + this.ID*10;
    //document.write(JSON.stringify(this.ID))
    if (indx >= this.numberStudents) {

      //document.write(JSON.stringify(indx));
      //document.write(JSON.stringify(this.numberStudents));
      //document.write(JSON.stringify(indx >= this.numberStudents));
      
      this.stdnt_ID_5 = "- - - - -";
      this.spacy_5 = "- - -";
      this.bert_5 = "- - -";
    }else{

      //document.write(JSON.stringify(indx));
      //document.write(JSON.stringify(this.numberStudents));
      //document.write(JSON.stringify(indx >= this.numberStudents));

      var Plentas = JSON.parse(JSON.stringify(JSON.parse(this.evaluation)[4 + this.ID*10])); 
      this.stdnt_ID_5 = JSON.stringify(Plentas[indx.toString()]["ID"]);
      this.spacy_5 = JSON.stringify(Plentas[indx.toString()]["NotaSpacy"]);
      this.bert_5 = JSON.stringify(Plentas[indx.toString()]["NotaBert"]);
    }

     
    var indx = 5 + this.ID*10;
    //document.write(JSON.stringify(this.ID))

    if (indx >= this.numberStudents) {
      this.stdnt_ID_6 = "- - - - -";
      this.spacy_6 = "- - -";
      this.bert_6 = "- - -";
    }else{
      var Plentas = JSON.parse(JSON.stringify(JSON.parse(this.evaluation)[5 + this.ID*10]));
      this.stdnt_ID_6 = JSON.stringify(Plentas[indx.toString()]["ID"]);
      this.spacy_6 = JSON.stringify(Plentas[indx.toString()]["NotaSpacy"]);
      this.bert_6 = JSON.stringify(Plentas[indx.toString()]["NotaBert"]);
    }

    
    var indx = 6 + this.ID*10;

    if (indx >= this.numberStudents) {
      this.stdnt_ID_7 = "- - - - -";
      this.spacy_7 = "- - -";
      this.bert_7 = "- - -";
    }else{
      var Plentas = JSON.parse(JSON.stringify(JSON.parse(this.evaluation)[6 + this.ID*10])); 
      this.stdnt_ID_7 = JSON.stringify(Plentas[indx.toString()]["ID"]);
      this.spacy_7 = JSON.stringify(Plentas[indx.toString()]["NotaSpacy"]);
      this.bert_7 = JSON.stringify(Plentas[indx.toString()]["NotaBert"]);
    }

    
    var indx = 7 + this.ID*10;

    if (indx >= this.numberStudents) {
      this.stdnt_ID_8 = "- - - - -";
      this.spacy_8 = "- - -";
      this.bert_8 = "- - -";
    }else{
      var Plentas = JSON.parse(JSON.stringify(JSON.parse(this.evaluation)[7 + this.ID*10])); 
      this.stdnt_ID_8 = JSON.stringify(Plentas[indx.toString()]["ID"]);
      this.spacy_8 = JSON.stringify(Plentas[indx.toString()]["NotaSpacy"]);
      this.bert_8 = JSON.stringify(Plentas[indx.toString()]["NotaBert"]);
    }
    
    var indx = 8 + this.ID*10;

    if (indx >= this.numberStudents) {
      this.stdnt_ID_9 = "- - - - -";
      this.spacy_9 = "- - -";
      this.bert_9 = "- - -";
    }else{
      var Plentas = JSON.parse(JSON.stringify(JSON.parse(this.evaluation)[8 + this.ID*10])); 
      this.stdnt_ID_9 = JSON.stringify(Plentas[indx.toString()]["ID"]);
      this.spacy_9 = JSON.stringify(Plentas[indx.toString()]["NotaSpacy"]);
      this.bert_9 = JSON.stringify(Plentas[indx.toString()]["NotaBert"]);
    }

     
    var indx = 9 + this.ID*10;

    if (indx >= this.numberStudents) {
      this.stdnt_ID_10 = "- - - - -";
      this.spacy_10 = "- - -";
      this.bert_10 = "- - -";
    }else{
      var Plentas = JSON.parse(JSON.stringify(JSON.parse(this.evaluation)[9 + this.ID*10]));
      this.stdnt_ID_10 = JSON.stringify(Plentas[indx.toString()]["ID"]);
      this.spacy_10 = JSON.stringify(Plentas[indx.toString()]["NotaSpacy"]);
      this.bert_10 = JSON.stringify(Plentas[indx.toString()]["NotaBert"]);
    }


  }

  showPreviousStudent() {
    //this.experimentDataService2.outputData = JSON.stringify(this.evaluation["message3"], null, 3);
    this.ID-=1;
    if (this.ID < 0) {
      this.ID = 0;
    }
    
    this.ID_show = this.ID +1
    
    //this.experimentDataService2.outputData = JSON.stringify(this.evaluation)[this.ID];
    
    this.updateTable()

  }
  showNextStudent() {
    //this.experimentDataService2.outputData = JSON.stringify(this.evaluation["message3"], null, 3);

    this.ID -=1
    this.ID +=2
    
    if (this.ID *10 >= this.numberStudents) {
      this.ID -=1
    }
    
    this.ID_show = this.ID +1

    

    //this.experimentDataService2.outputData = JSON.parse(this.evaluation)[this.ID]["ID"];
    this.updateTable()

    //document.write(JSON.stringify(obj2[a][id]));  
    //this.experimentDataService2.outputData = JSON.stringify(this.evaluation, null, 3);  

  }


  copyToClipboard(text: string) {
    const selBox = document.createElement('textarea');
    selBox.style.position = 'fixed';
    selBox.style.left = '0';
    selBox.style.top = '0';
    selBox.style.opacity = '0';
    selBox.value = text;
    document.body.appendChild(selBox);
    selBox.focus();
    selBox.select();
    document.execCommand('copy');
    document.body.removeChild(selBox);
    this.toastr.success('Datos copiados al portapapeles.');
  }
}



