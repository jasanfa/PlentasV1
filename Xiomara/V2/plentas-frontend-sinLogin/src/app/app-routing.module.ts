import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ConfigurationComponent } from './pages/configuration/configuration.component';
import { Configuration2Component } from './pages/configuration2/configuration2.component';
import { HomeComponent } from './pages/home/home.component';
import { OutputComponent } from './pages/output/output.component';
import { ResultsComponent } from './pages/results/results.component';

const routes: Routes = [
  {
    path: 'home',
    component: HomeComponent
  },
  {
    path: 'configuration',
    component: ConfigurationComponent
  },
  {
    path: 'configuration2',
    component: Configuration2Component
  },
  {
    path: 'output',
    component: OutputComponent
  },
  {
    path: 'results',
    component: ResultsComponent
  },  
  {
    path: '**',
    component: HomeComponent
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }