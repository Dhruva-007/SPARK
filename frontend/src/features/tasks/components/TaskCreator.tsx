/**
 * SPARK — Task Creator Modal
 */

import React, { useState } from "react";
import { Plus, Zap } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";
import { Modal, ModalFooter } from "@shared/components/ui/Modal";
import { Input, Textarea } from "@shared/components/ui/Input";
import { Button } from "@shared/components/ui/Button";
import { useCreateTask } from "@shared/hooks/useApi";
import { useTaskStore } from "@shared/stores/task.store";
import { useToast } from "@shared/stores/ui.store";
import type {
  CreateTaskRequest,
  TaskCategory,
  TaskPriority,
  TaskComplexity,
} from "@shared/types/task.types";

const CATEGORIES: { value: TaskCategory; label: string }[] = [
  { value: "academic", label: "Academic" },
  { value: "work", label: "Work" },
  { value: "personal", label: "Personal" },
];

const PRIORITIES: { value: TaskPriority; label: string }[] = [
  { value: "critical", label: "Critical" },
  { value: "high", label: "High" },
  { value: "medium", label: "Medium" },
  { value: "low", label: "Low" },
];

const COMPLEXITIES: { value: TaskComplexity; label: string }[] = [
  { value: "low", label: "Low" },
  { value: "medium", label: "Medium" },
  { value: "high", label: "High" },
];

export const TaskCreator: React.FC = () => {
  const { createTaskModalOpen, closeCreateTaskModal } = useTaskStore();
  const createTask = useCreateTask();
  const toast = useToast();
  const queryClient = useQueryClient();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState<TaskCategory>("work");
  const [priority, setPriority] = useState<TaskPriority>("medium");
  const [complexity, setComplexity] = useState<TaskComplexity>("medium");
  const [deadline, setDeadline] = useState("");
  const [estimatedHours, setEstimatedHours] = useState("4");
  const [errors, setErrors] = useState<Record<string, string>>({});

  const resetForm = () => {
    setTitle("");
    setDescription("");
    setCategory("work");
    setPriority("medium");
    setComplexity("medium");
    setDeadline("");
    setEstimatedHours("4");
    setErrors({});
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!title.trim()) newErrors.title = "Title is required";
    if (!deadline) newErrors.deadline = "Deadline is required";
    if (!estimatedHours || parseFloat(estimatedHours) <= 0)
      newErrors.estimatedHours = "Must be a positive number";

    if (deadline) {
      const deadlineDate = new Date(deadline);
      if (deadlineDate <= new Date())
        newErrors.deadline = "Deadline must be in the future";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;

    const request: CreateTaskRequest = {
      title: title.trim(),
      description: description.trim(),
      category,
      priority,
      complexity,
      deadline: new Date(deadline).toISOString(),
      estimatedHours: parseFloat(estimatedHours),
      tags: [],
    };

    try {
      await createTask.mutateAsync(request);
      toast.success(
        "Task created",
        "SPARK is generating milestones in the background..."
      );
      resetForm();
      closeCreateTaskModal();

      // Re-fetch task list after delay to pick up async milestones
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ["tasks"] });
        queryClient.invalidateQueries({ queryKey: ["analytics"] });
      }, 8000);
    } catch (err) {
      toast.error(
        "Failed to create task",
        err instanceof Error ? err.message : "Unknown error"
      );
    }
  };

  return (
    <Modal
      open={createTaskModalOpen}
      onClose={closeCreateTaskModal}
      title="Create New Task"
      description="SPARK will immediately generate an AI execution plan"
      size="lg"
    >
      <div className="space-y-5">
        <Input
          label="Task Title"
          placeholder="e.g., Write Research Paper on Climate Change"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          error={errors.title}
        />

        <Textarea
          label="Description (optional)"
          placeholder="What needs to be accomplished?"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />

        <div className="grid grid-cols-3 gap-4">
          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-text-primary">
              Category
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value as TaskCategory)}
              className="input"
            >
              {CATEGORIES.map((c) => (
                <option key={c.value} value={c.value}>{c.label}</option>
              ))}
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-text-primary">
              Priority
            </label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value as TaskPriority)}
              className="input"
            >
              {PRIORITIES.map((p) => (
                <option key={p.value} value={p.value}>{p.label}</option>
              ))}
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-text-primary">
              Complexity
            </label>
            <select
              value={complexity}
              onChange={(e) => setComplexity(e.target.value as TaskComplexity)}
              className="input"
            >
              {COMPLEXITIES.map((c) => (
                <option key={c.value} value={c.value}>{c.label}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Deadline"
            type="datetime-local"
            value={deadline}
            onChange={(e) => setDeadline(e.target.value)}
            error={errors.deadline}
          />
          <Input
            label="Estimated Hours"
            type="number"
            min="0.5"
            step="0.5"
            value={estimatedHours}
            onChange={(e) => setEstimatedHours(e.target.value)}
            error={errors.estimatedHours}
          />
        </div>

        <div className="flex items-center gap-2 px-3 py-2 bg-accent-light/50 rounded-lg">
          <Zap className="w-3.5 h-3.5 text-accent" />
          <span className="text-xs text-accent font-medium">
            SPARK will auto-generate milestones and an activation package
          </span>
        </div>
      </div>

      <ModalFooter>
        <Button variant="secondary" onClick={closeCreateTaskModal}>
          Cancel
        </Button>
        <Button
          variant="primary"
          onClick={handleSubmit}
          loading={createTask.isPending}
          icon={<Plus className="w-4 h-4" />}
        >
          Create Task
        </Button>
      </ModalFooter>
    </Modal>
  );
};

TaskCreator.displayName = "TaskCreator";