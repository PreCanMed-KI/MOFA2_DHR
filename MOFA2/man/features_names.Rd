% Generated by roxygen2: do not edit by hand
% Please edit documentation in R/AllGenerics.R, R/set_methods.R
\name{features_names}
\alias{features_names}
\alias{features_names<-}
\alias{features_names,MOFA-method}
\alias{features_names<-,MOFA,list-method}
\title{features_names: set and retrieve feature names}
\usage{
features_names(object)

features_names(object) <- value

\S4method{features_names}{MOFA}(object)

\S4method{features_names}{MOFA,list}(object) <- value
}
\arguments{
\item{object}{a \code{\link{MOFA}} object.}

\item{value}{list of character vectors with the feature names for every view}
}
\value{
list of character vectors with the feature names for each view
}
\description{
features_names: set and retrieve feature names
}
