output "vpc_id"            { value = module.vpc.vpc_id }
output "eks_cluster_name"  { value = module.eks.cluster_name }
output "configure_kubectl" { value = "aws eks update-kubeconfig --region us-east-1 --name ${module.eks.cluster_name}" }
