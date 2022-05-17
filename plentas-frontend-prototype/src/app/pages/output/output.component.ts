import { Component, OnInit } from '@angular/core';
import { ToastrService } from 'ngx-toastr';
import { ExperimentDataService } from 'src/app/services/experiment-data.service';

@Component({
  selector: 'app-output',
  templateUrl: './output.component.html',
  styleUrls: ['./output.component.css']
})
export class OutputComponent implements OnInit {

  constructor(public experimentDataService: ExperimentDataService, private toastr: ToastrService) { }

  ngOnInit(): void {
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
