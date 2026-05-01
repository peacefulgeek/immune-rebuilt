import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import Home from "./pages/Home";
import Articles from "./pages/Articles";
import Article from "./pages/Article";
import About from "./pages/About";
import Disclosures from "./pages/Disclosures";
import Privacy from "./pages/Privacy";
import Contact from "./pages/Contact";
import { AssessmentsIndex, AssessmentDetail } from "./pages/Assessments";
import Apothecary from "./pages/Apothecary";
import NotFound from "./pages/NotFound";
import SiteShell from "./components/SiteShell";

function Router() {
  return (
    <Switch>
      <Route path="/" component={Home} />
      <Route path="/articles" component={Articles} />
      <Route path="/articles/:slug" component={Article} />
      <Route path="/about" component={About} />
      <Route path="/disclosures" component={Disclosures} />
      <Route path="/privacy" component={Privacy} />
      <Route path="/contact" component={Contact} />
      <Route path="/assessments" component={AssessmentsIndex} />
      <Route path="/assessments/:slug" component={AssessmentDetail} />
      <Route path="/apothecary" component={Apothecary} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider defaultTheme="light">
        <TooltipProvider>
          <Toaster richColors closeButton />
          <SiteShell>
            <Router />
          </SiteShell>
        </TooltipProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
