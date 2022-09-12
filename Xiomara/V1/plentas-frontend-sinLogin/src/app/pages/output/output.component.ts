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
  ID = 1;

  constructor(public experimentDataService: ExperimentDataService, public experimentDataService2: ExperimentDataServiceFeedback, public bufferEvaluation: BufferEvaluation, private toastr: ToastrService) { }

  ngOnInit(): void {
    this.evaluation = this.bufferEvaluation.outputData;

  }


  showPreviousStudent() {
    //this.experimentDataService2.outputData = JSON.stringify(this.evaluation["message3"], null, 3);
    this.ID-=1;
    if (this.ID <= 0) {
      this.ID = 1;
    } 
    this.experimentDataService2.outputData = JSON.parse(this.evaluation)[this.ID]; 
    //this.experimentDataService2.outputData = JSON.stringify(this.evaluation)[this.ID];   

  }
  showNextStudent() {
    //this.experimentDataService2.outputData = JSON.stringify(this.evaluation["message3"], null, 3);
    this.ID -=1
    this.ID +=2 
    this.experimentDataService2.outputData = JSON.parse(this.evaluation)[this.ID];

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
