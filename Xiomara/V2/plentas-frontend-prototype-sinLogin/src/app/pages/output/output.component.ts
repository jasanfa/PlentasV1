import { Component, OnInit } from '@angular/core';
import { ToastrService } from 'ngx-toastr';
import { ExperimentDataService } from 'src/app/services/experiment-data.service';
import { ExperimentDataServiceFeedback } from 'src/app/services/experiment-data.service2';
import { BufferEvaluation } from 'src/app/services/experiment-data.bufferEvaluacion';
import { ConfigVariables } from 'src/app/services/configurationVariables';

import * as XLSX from 'xlsx'



@Component({
  selector: 'app-output',
  templateUrl: './output.component.html',
  styleUrls: ['./output.component.css']
})
export class OutputComponent implements OnInit {

  evaluation:any;
  excel:any;
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

  bert_semantica = 0;
  sintaxis = 0;
  ortografia = 0;
  spacy_semantica = 0;
  
  desglose_semantica_spacy = "---";
  desglose_semantica_bert= "---";
  desglose_sintaxis= "---";
  desglose_ortografia= "---";

  peso_config_semantica = 0;
  peso_config_sintaxis = 0;
  peso_config_orto = 0;

  activado_semantica = false;
  activado_ortografia = false;
  activado_sintaxis = false;

  

  constructor(public experimentDataService: ExperimentDataService, public experimentDataService2: ExperimentDataServiceFeedback, public bufferEvaluation: BufferEvaluation, private toastr: ToastrService, private variables: ConfigVariables) { }

  ngOnInit(): void {
    //document.write(JSON.stringify(JSON.parse(this.bufferEvaluation.outputData)[0]))

    //this.evaluation = this.bufferEvaluation.outputData[0];
    this.evaluation = JSON.stringify(JSON.parse(this.bufferEvaluation.outputData)[0])
    this.excel = JSON.parse(this.bufferEvaluation.outputData)[1]
    
    this.numberStudents = JSON.parse(this.evaluation).length;
    this.updateTable();
    this.ID_show = this.ID + 1;  
    this.peso_config_semantica = this.variables.semanticValue;
    this.peso_config_sintaxis = this.variables.syntaxValue;
    this.peso_config_orto = this.variables.orthographyValue;
    this.activado_ortografia = this.variables.checkOrthography;
    this.activado_sintaxis = this.variables.checkSyntax;
    this.activado_semantica = this.variables.checkSemantic;


  }

  showFeedback(tableIndx:any){
    //document.write("blabla");
    var fdbckIndx = tableIndx + this.ID*10;
    var Plentas = JSON.parse(JSON.stringify(JSON.parse(this.evaluation)[fdbckIndx]));     
    this.experimentDataService2.outputData = JSON.parse(JSON.stringify(Plentas[fdbckIndx.toString()]["Feedback"]));

    //Esto es el desglose de la rubrica
    if (this.activado_ortografia){
      this.ortografia = Number(JSON.parse(JSON.stringify(Plentas[fdbckIndx.toString()]["NotaOrtografia"])).toFixed(2));
      
      this.desglose_ortografia = JSON.stringify(((this.ortografia / this.peso_config_orto) *10).toFixed(2)) + "   (" + JSON.stringify(this.ortografia) + " / " + JSON.stringify(this.peso_config_orto) + ")";
    }else{
      this.desglose_ortografia= "---";
    }

    if (this.activado_sintaxis){
      this.sintaxis = Number(JSON.parse(JSON.stringify(Plentas[fdbckIndx.toString()]["NotaSintaxis"])).toFixed(2));
      
      this.desglose_sintaxis = JSON.stringify(((this.sintaxis / this.peso_config_sintaxis) *10).toFixed(2)) + "   (" + JSON.stringify(this.sintaxis) + " / " + JSON.stringify(this.peso_config_sintaxis) + ")";
    }else{
      this.desglose_sintaxis= "---";
    }
    
    if (this.activado_semantica){
      this.bert_semantica = Number(JSON.parse(JSON.stringify(Plentas[fdbckIndx.toString()]["NotaSemanticaBert"])).toFixed(2));

      this.spacy_semantica = Number(JSON.parse(JSON.stringify(Plentas[fdbckIndx.toString()]["NotaSemanticaSpacy"])).toFixed(2));
      
      this.desglose_semantica_spacy = JSON.stringify(((this.spacy_semantica / this.peso_config_semantica) *10).toFixed(2)) + "   (" + JSON.stringify(this.spacy_semantica) + " / " + JSON.stringify(this.peso_config_semantica) + ")";
      
      this.desglose_semantica_bert = JSON.stringify(((this.bert_semantica / this.peso_config_semantica) *10).toFixed(2)) + "   (" + JSON.stringify(this.bert_semantica) + " / " + JSON.stringify(this.peso_config_semantica) + ")";
    }else{
      this.desglose_semantica_spacy= "---";
      this.desglose_semantica_bert= "---";
    }

    
  }
  
  
  ExportData(){

    var wb = XLSX.utils.book_new();
    wb.Props = {
    Title: "PLeNTaS Evaluation",
    Subject: "PLeNTaS",
    Author: "PLeNTaS",
    };

    wb.SheetNames.push("PLeNTaS-Eval");
    let ws_data = new Array();
    let aux_array = new Array();

    
    for ( var key in this.excel ) {
      aux_array.push(key)      
    }
    ws_data.push(aux_array)
    aux_array = new Array();

    var student_id = 0
    while(student_id != this.numberStudents){
      for ( var key in this.excel ) {
        aux_array.push(this.excel[key][student_id])
     
      }
      ws_data.push(aux_array)
      aux_array = new Array(); 
      student_id = student_id + 1
    }
    
    var ws = XLSX.utils.aoa_to_sheet(ws_data);
    wb.Sheets["PLeNTaS-Eval"] = ws;
    //XLSX.utils.book_append_sheet(wb, ws, 'Sheet1');

    /* save to file */  
    XLSX.writeFile(wb, "PLeNTaS Evaluation.xlsx");
    
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
      this.spacy_1 = JSON.stringify((Plentas[indx.toString()]["SimilitudSpacy"]*10).toFixed(2)) + " / 10";
      this.bert_1 = JSON.stringify((Plentas[indx.toString()]["SimilitudBert"]*10).toFixed(2)) + " / 10";
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
      this.spacy_2 = JSON.stringify((Plentas[indx.toString()]["SimilitudSpacy"]*10).toFixed(2)) + " / 10";
      this.bert_2 = JSON.stringify((Plentas[indx.toString()]["SimilitudBert"]*10).toFixed(2)) + " / 10";

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
      this.spacy_3 = JSON.stringify((Plentas[indx.toString()]["SimilitudSpacy"]*10).toFixed(2)) + " / 10";
      this.bert_3 = JSON.stringify((Plentas[indx.toString()]["SimilitudBert"]*10).toFixed(2)) + " / 10";
    }

    
    var indx = 3 + this.ID*10;

    if (indx >= this.numberStudents) {
      this.stdnt_ID_4 = "- - - - -";
      this.spacy_4 = "- - -";
      this.bert_4 = "- - -";
      
    }else{
      var Plentas = JSON.parse(JSON.stringify(JSON.parse(this.evaluation)[3 + this.ID*10])); 
      this.stdnt_ID_4 = JSON.stringify(Plentas[indx.toString()]["ID"]);
      this.spacy_4 = JSON.stringify((Plentas[indx.toString()]["SimilitudSpacy"]*10).toFixed(2)) + " / 10";
      this.bert_4 = JSON.stringify((Plentas[indx.toString()]["SimilitudBert"]*10).toFixed(2)) + " / 10";
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
      this.spacy_5 = JSON.stringify((Plentas[indx.toString()]["SimilitudSpacy"]*10).toFixed(2)) + " / 10";
      this.bert_5 = JSON.stringify((Plentas[indx.toString()]["SimilitudBert"]*10).toFixed(2)) + " / 10";
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
      this.spacy_6 = JSON.stringify((Plentas[indx.toString()]["SimilitudSpacy"]*10).toFixed(2)) + " / 10";
      this.bert_6 = JSON.stringify((Plentas[indx.toString()]["SimilitudBert"]*10).toFixed(2)) + " / 10";
    }

    
    var indx = 6 + this.ID*10;

    if (indx >= this.numberStudents) {
      this.stdnt_ID_7 = "- - - - -";
      this.spacy_7 = "- - -";
      this.bert_7 = "- - -";
    }else{
      var Plentas = JSON.parse(JSON.stringify(JSON.parse(this.evaluation)[6 + this.ID*10])); 
      this.stdnt_ID_7 = JSON.stringify(Plentas[indx.toString()]["ID"]);
      this.spacy_7 = JSON.stringify((Plentas[indx.toString()]["SimilitudSpacy"]*10).toFixed(2)) + " / 10";
      this.bert_7 = JSON.stringify((Plentas[indx.toString()]["SimilitudBert"]*10).toFixed(2)) + " / 10";
    }

    
    var indx = 7 + this.ID*10;

    if (indx >= this.numberStudents) {
      this.stdnt_ID_8 = "- - - - -";
      this.spacy_8 = "- - -";
      this.bert_8 = "- - -";
    }else{
      var Plentas = JSON.parse(JSON.stringify(JSON.parse(this.evaluation)[7 + this.ID*10])); 
      this.stdnt_ID_8 = JSON.stringify(Plentas[indx.toString()]["ID"]);
      this.spacy_8 = JSON.stringify((Plentas[indx.toString()]["SimilitudSpacy"]*10).toFixed(2)) + " / 10";
      this.bert_8 = JSON.stringify((Plentas[indx.toString()]["SimilitudBert"]*10).toFixed(2)) + " / 10";
    }
    
    var indx = 8 + this.ID*10;

    if (indx >= this.numberStudents) {
      this.stdnt_ID_9 = "- - - - -";
      this.spacy_9 = "- - -";
      this.bert_9 = "- - -";
    }else{
      var Plentas = JSON.parse(JSON.stringify(JSON.parse(this.evaluation)[8 + this.ID*10])); 
      this.stdnt_ID_9 = JSON.stringify(Plentas[indx.toString()]["ID"]);
      this.spacy_9 = JSON.stringify((Plentas[indx.toString()]["SimilitudSpacy"] *10).toFixed(2)) + " / 10";
      this.bert_9 = JSON.stringify((Plentas[indx.toString()]["SimilitudBert"]*10).toFixed(2)) + " / 10";
    }

     
    var indx = 9 + this.ID*10;

    if (indx >= this.numberStudents) {
      this.stdnt_ID_10 = "- - - - -";
      this.spacy_10 = "- - -";
      this.bert_10 = "- - -";
    }else{
      var Plentas = JSON.parse(JSON.stringify(JSON.parse(this.evaluation)[9 + this.ID*10]));
      this.stdnt_ID_10 = JSON.stringify(Plentas[indx.toString()]["ID"]);
      this.spacy_10 = JSON.stringify((Plentas[indx.toString()]["SimilitudSpacy"]*10).toFixed(2)) + " / 10";
      this.bert_10 = JSON.stringify((Plentas[indx.toString()]["SimilitudBert"]*10).toFixed(2)) + " / 10";
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



