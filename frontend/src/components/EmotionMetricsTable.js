import React from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Box,
  useTheme,
} from "@mui/material";
import { styled } from "@mui/material/styles";

const StyledTableCell = styled(TableCell)(({ theme }) => ({
  padding: theme.spacing(3),
  borderBottom: `2px solid ${theme.palette.divider}`,
  "&.MuiTableCell-head": {
    background: "#ff4d4d",  // Matching your app's coral/red theme
    color: theme.palette.common.white,
    fontWeight: "bold",
    fontSize: "1.4rem",
    textTransform: "uppercase",
    letterSpacing: "1px",
  },
  "&.MuiTableCell-body": {
    fontSize: "1.2rem",
    color: theme.palette.text.primary,
  },
}));

const StyledTableRow = styled(TableRow)(({ theme }) => ({
  "&:nth-of-type(odd)": {
    backgroundColor: "rgba(255, 77, 77, 0.05)",  // Very light coral for alternating rows
  },
  "&:hover": {
    backgroundColor: "rgba(255, 77, 77, 0.1)",  // Slightly darker on hover
    transform: "scale(1.01)",
    transition: "transform 0.2s ease-in-out",
  },
  transition: "all 0.2s ease-in-out",
}));

const MetricValue = styled(Box)(({ theme, value }) => ({
  display: "inline-block",
  padding: theme.spacing(1, 2),
  borderRadius: theme.spacing(1),
  backgroundColor: value >= 0.8
    ? "#4CAF50"  // Success green
    : value >= 0.6
    ? "#FFA726"  // Warning orange
    : "#F44336",  // Error red
  color: theme.palette.common.white,
  fontWeight: "bold",
  minWidth: "80px",
  fontSize: "1.2rem",
  textAlign: "center",
}));

const EmotionMetricsTable = () => {
  const theme = useTheme();

  const metrics = [
    {
      category: "Text-based Emotion Recognition",
      metrics: [
        { name: "Accuracy", value: 0.85 },
        { name: "Precision", value: 0.82 },
        { name: "Recall", value: 0.88 },
        { name: "F1 Score", value: 0.85 },
      ],
    },
    {
      category: "Facial Emotion Recognition",
      metrics: [
        { name: "Accuracy", value: 0.78 },
        { name: "Precision", value: 0.75 },
        { name: "Recall", value: 0.80 },
        { name: "F1 Score", value: 0.77 },
      ],
    },
    {
      category: "Speech-based Emotion Recognition",
      metrics: [
        { name: "Accuracy", value: 0.72 },
        { name: "Precision", value: 0.70 },
        { name: "Recall", value: 0.74 },
        { name: "F1 Score", value: 0.72 },
      ],
    },
  ];

  return (
    <TableContainer
      component={Paper}
      elevation={6}
      sx={{
        borderRadius: 4,
        overflow: "hidden",
        margin: theme.spacing(4, 0),
        background: theme.palette.background.paper,
        width: "90%",
        maxWidth: "1200px",
        marginLeft: "auto",
        marginRight: "auto",
        "& .MuiTable-root": {
          borderCollapse: "separate",
          borderSpacing: "0 8px",
        }
      }}
    >
      <Table>
        <TableHead>
          <TableRow>
            <StyledTableCell>Category</StyledTableCell>
            <StyledTableCell>Metric</StyledTableCell>
            <StyledTableCell align="right">Value</StyledTableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {metrics.map((category, categoryIndex) => (
            <React.Fragment key={categoryIndex}>
              <StyledTableRow>
                <StyledTableCell
                  rowSpan={category.metrics.length + 1}
                  sx={{
                    background: "rgba(255, 77, 77, 0.9)",  // Matching your app's theme
                    color: "#ffffff",
                    fontWeight: "bold",
                    verticalAlign: "top",
                    fontSize: "1.3rem",
                  }}
                >
                  {category.category}
                </StyledTableCell>
              </StyledTableRow>
              {category.metrics.map((metric, metricIndex) => (
                <StyledTableRow key={metricIndex}>
                  <StyledTableCell>{metric.name}</StyledTableCell>
                  <StyledTableCell align="right">
                    <MetricValue value={metric.value}>
                      {(metric.value * 100).toFixed(1)}%
                    </MetricValue>
                  </StyledTableCell>
                </StyledTableRow>
              ))}
            </React.Fragment>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default EmotionMetricsTable; 