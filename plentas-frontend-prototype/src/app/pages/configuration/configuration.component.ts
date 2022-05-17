import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { ApiService } from 'src/app/services/api.service';
import { ExperimentDataService } from 'src/app/services/experiment-data.service';

@Component({
  selector: 'app-configuration',
  templateUrl: './configuration.component.html',
  styleUrls: ['./configuration.component.css'],
})
export class ConfigurationComponent implements OnInit {
  inputData = '';
  inputJsonFile: any = null;
  checkOrthography = false;
  checkSyntax = false;
  checkSemantic = false;
  public orthographyValue = 0.3;
  syntaxValue = 0.3;
  semanticValue = 0.4;

  constructor(
    private toastr: ToastrService,
    private apiService: ApiService,
    public experimentDataService: ExperimentDataService,
    private router: Router
  ) {}

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
        this.experimentDataService.outputData = JSON.stringify(outputDataObject, null, 3);
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
