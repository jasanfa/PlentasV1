import { Component, OnInit } from '@angular/core';
import { ToastrService } from 'ngx-toastr';
import { ApiService } from 'src/app/api.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
})
export class HomeComponent implements OnInit {
  inputData = '';
  outputData = '';

  constructor(private toastr: ToastrService, private apiService: ApiService) {}

  ngOnInit(): void {}

  async processInputData() {
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
        this.outputData = JSON.stringify(outputDataObject, null, 3);
      } else {
        this.toastr.error('No se han recibido datos de salida.');
      }
    } catch (error) {
      this.toastr.error(JSON.stringify(error), 'Error procesando datos', {disableTimeOut: true});
    }
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
